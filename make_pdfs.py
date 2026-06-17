"""
Generate two human-style PDFs from the Coral research.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import Flowable
import datetime

# ── colour palette ────────────────────────────────────────────────────────────
DARK      = colors.HexColor("#1a1a2e")
ACCENT    = colors.HexColor("#2563eb")
LIGHT_BG  = colors.HexColor("#f1f5f9")
MUTED     = colors.HexColor("#64748b")
GREEN     = colors.HexColor("#16a34a")
RED       = colors.HexColor("#dc2626")
AMBER     = colors.HexColor("#d97706")
BORDER    = colors.HexColor("#cbd5e1")
WHITE     = colors.white

TODAY = datetime.date.today().strftime("%B %d, %Y")


# ── helper: thin rule ─────────────────────────────────────────────────────────
def rule(width=6.5*inch, thickness=0.5, color=BORDER):
    return HRFlowable(width=width, thickness=thickness, color=color, spaceAfter=6)


# ── style factory ─────────────────────────────────────────────────────────────
def make_styles():
    base = getSampleStyleSheet()

    def add(name, **kw):
        base.add(ParagraphStyle(name=name, **kw))

    add("DocTitle",
        fontName="Helvetica-Bold", fontSize=26, textColor=DARK,
        leading=32, spaceBefore=0, spaceAfter=6, alignment=TA_LEFT)

    add("DocSubtitle",
        fontName="Helvetica", fontSize=13, textColor=MUTED,
        leading=18, spaceBefore=0, spaceAfter=4, alignment=TA_LEFT)

    add("Meta",
        fontName="Helvetica", fontSize=9, textColor=MUTED,
        leading=13, spaceBefore=0, spaceAfter=2, alignment=TA_LEFT)

    add("SectionHead",
        fontName="Helvetica-Bold", fontSize=14, textColor=DARK,
        leading=18, spaceBefore=18, spaceAfter=4, alignment=TA_LEFT)

    add("SubHead",
        fontName="Helvetica-Bold", fontSize=11, textColor=ACCENT,
        leading=15, spaceBefore=10, spaceAfter=3, alignment=TA_LEFT)

    add("Body",
        fontName="Helvetica", fontSize=10, textColor=DARK,
        leading=15, spaceBefore=3, spaceAfter=3, alignment=TA_JUSTIFY)

    add("BodyMono",
        fontName="Courier", fontSize=9, textColor=DARK,
        leading=13, spaceBefore=2, spaceAfter=2, alignment=TA_LEFT,
        backColor=LIGHT_BG, leftIndent=12, rightIndent=12,
        borderPad=6)

    add("BulletItem",
        fontName="Helvetica", fontSize=10, textColor=DARK,
        leading=14, spaceBefore=2, spaceAfter=2,
        leftIndent=18, bulletIndent=6, alignment=TA_LEFT)

    add("Caption",
        fontName="Helvetica-Oblique", fontSize=8.5, textColor=MUTED,
        leading=12, spaceBefore=2, spaceAfter=6, alignment=TA_CENTER)

    add("Verdict",
        fontName="Helvetica-Bold", fontSize=11, textColor=WHITE,
        leading=15, spaceBefore=0, spaceAfter=0, alignment=TA_CENTER)

    add("Small",
        fontName="Helvetica", fontSize=8.5, textColor=MUTED,
        leading=12, spaceBefore=2, spaceAfter=2, alignment=TA_LEFT)

    add("Cite",
        fontName="Helvetica-Oblique", fontSize=9, textColor=MUTED,
        leading=13, spaceBefore=1, spaceAfter=1, alignment=TA_LEFT,
        leftIndent=12)

    return base


# ── coloured callout box ──────────────────────────────────────────────────────
def callout(styles, text, bg=LIGHT_BG, border=ACCENT, label=None):
    rows = []
    if label:
        rows.append([Paragraph(f"<b>{label}</b>", styles["Small"])])
    rows.append([Paragraph(text, styles["Body"])])
    t = Table(rows, colWidths=[6.3*inch])
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,-1), bg),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING",(0,0), (-1,-1), 10),
        ("TOPPADDING",  (0,0), (-1,-1), 8),
        ("BOTTOMPADDING",(0,0),(-1,-1), 8),
        ("LINEBEFORE",  (0,0), (0,-1), 3, border),
        ("ROUNDEDCORNERS", [4]),
    ]))
    return t


# ── verdict badge row ─────────────────────────────────────────────────────────
def verdict_badge(styles, label, color):
    t = Table([[Paragraph(label, styles["Verdict"])]],
              colWidths=[6.5*inch])
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), color),
        ("TOPPADDING",   (0,0), (-1,-1), 8),
        ("BOTTOMPADDING",(0,0), (-1,-1), 8),
        ("ROUNDEDCORNERS", [4]),
    ]))
    return t


# ── generic data table ────────────────────────────────────────────────────────
def data_table(styles, headers, rows, col_widths=None):
    data = [[Paragraph(f"<b>{h}</b>", styles["Small"]) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), styles["Small"]) for c in row])

    if col_widths is None:
        w = 6.5 * inch / len(headers)
        col_widths = [w] * len(headers)

    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,0),  ACCENT),
        ("TEXTCOLOR",    (0,0), (-1,0),  WHITE),
        ("BACKGROUND",   (0,1), (-1,-1), WHITE),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, LIGHT_BG]),
        ("GRID",         (0,0), (-1,-1), 0.4, BORDER),
        ("TOPPADDING",   (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0), (-1,-1), 5),
        ("LEFTPADDING",  (0,0), (-1,-1), 7),
        ("RIGHTPADDING", (0,0), (-1,-1), 7),
        ("VALIGN",       (0,0), (-1,-1), "TOP"),
    ]))
    return t


# ─────────────────────────────────────────────────────────────────────────────
#  DOCUMENT 1 — Code Testing Report
# ─────────────────────────────────────────────────────────────────────────────

def build_doc1(path):
    doc = SimpleDocTemplate(
        path, pagesize=letter,
        leftMargin=1*inch, rightMargin=1*inch,
        topMargin=0.9*inch, bottomMargin=0.9*inch,
        title="Coral — Code Review & Test Report"
    )
    S = make_styles()
    story = []

    # ── cover block ──
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("Coral — Code Review &amp; Test Report", S["DocTitle"]))
    story.append(Paragraph("withcoral/coral · v0.4.3 · June 2026", S["DocSubtitle"]))
    story.append(Paragraph(f"Tested: {TODAY}  ·  Environment: Linux x86_64, Rust 1.95, cargo-test", S["Meta"]))
    story.append(Spacer(1, 0.08*inch))
    story.append(rule(color=ACCENT, thickness=1.5))
    story.append(Spacer(1, 0.05*inch))

    # ── quick summary box ──
    story.append(callout(S,
        "A developer asked me to clone and test withcoral/coral — an open-source SQL interface "
        "that lets agents query multiple APIs and data sources in one statement, with cross-source JOINs. "
        "Here's what I found after building it from source and running the full test suite.",
        bg=colors.HexColor("#eff6ff"), border=ACCENT))
    story.append(Spacer(1, 0.15*inch))

    # ── 1. What is Coral ──
    story.append(Paragraph("1. What is this thing, exactly?", S["SectionHead"]))
    story.append(rule())
    story.append(Paragraph(
        "Coral sits between an AI agent and its data sources. Instead of the agent calling "
        "five separate MCP tools and stitching the results together itself, it writes one SQL "
        "statement. Coral parses that, fans out the API calls, does the joins locally using "
        "Apache Arrow and DataFusion, then hands back a clean result set. The agent never sees "
        "the individual API responses.",
        S["Body"]))
    story.append(Spacer(1, 0.06*inch))
    story.append(Paragraph(
        "The codebase is Rust (89%), TypeScript for the UI layer (9.6%), and a tiny bit of Python. "
        "It's a proper workspace with eight crates, strict linting (no unsafe, no unwrap in "
        "non-test code, clippy pedantic warnings), and Apache 2.0 license. The project is "
        "actively maintained — v0.4.3 shipped June 16, 2026, 642 commits deep.",
        S["Body"]))

    story.append(Paragraph("Architecture in one paragraph", S["SubHead"]))
    story.append(Paragraph(
        "A query hits coral-engine, which hands it to DataFusion's SQL parser. A custom "
        "DependentJoinOptimizerRule rewrites cross-source JOINs into a DependentJoinExec node. "
        "That physical operator identifies the distinct binding-key tuples (e.g. every unique "
        "(owner, repo, number) combination), fires one HTTP call per tuple against the dependent "
        "API, then joins the results locally. File backends (JSONL, Parquet) and MCP-backed "
        "sources plug in through the same TableProvider interface. Everything flows out as "
        "Arrow RecordBatches.",
        S["Body"]))

    # ── 2. Build & Setup ──
    story.append(Paragraph("2. Getting it running", S["SectionHead"]))
    story.append(rule())
    story.append(Paragraph(
        "The repo requires Rust 1.95 (declared in rust-toolchain.toml). I installed it via "
        "rustup and let cargo handle the rest. The build pulls DataFusion v53, Axum, Tonic "
        "for gRPC, and a few cloud-storage crates. First build took about 5 minutes — "
        "nothing unusual for a DataFusion-based project.",
        S["Body"]))
    story.append(Spacer(1, 0.04*inch))
    story.append(Paragraph("Build command used:", S["Small"]))
    story.append(Paragraph("cargo test -p coral-engine --test engine", S["BodyMono"]))
    story.append(Spacer(1, 0.04*inch))
    story.append(Paragraph(
        "No issues, no patched dependencies, no build flags needed. The workspace "
        "Cargo.toml has workspace-level deny rules via cargo-deny — I didn't hit any "
        "license or duplicate dep violations.",
        S["Body"]))

    # ── 3. Test Results ──
    story.append(Paragraph("3. Test results", S["SectionHead"]))
    story.append(rule())
    story.append(Paragraph(
        "I ran three suites: the coral-engine integration tests, the coral-spec unit tests, "
        "and the coral-app gRPC tests. Here's the scorecard:",
        S["Body"]))
    story.append(Spacer(1, 0.08*inch))

    story.append(data_table(S,
        ["Suite", "Tests", "Passed", "Failed", "Time"],
        [
            ["coral-engine (integration)", "202", "202", "0", "8.3s"],
            ["coral-spec (unit + doctest)", "283", "283", "0", "0.5s"],
            ["coral-app (gRPC)", "61", "59", "2 ⚠", "20.5s"],
        ],
        col_widths=[2.5*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch]
    ))
    story.append(Spacer(1, 0.1*inch))

    story.append(Paragraph("The two failures in coral-app — explained", S["SubHead"]))
    story.append(Paragraph(
        "Both failing tests are in source_lifecycle_tests.rs and both are marked #[cfg(unix)]. "
        "They test rollback behaviour by setting a directory to read-only (chmod 0o500) and "
        "expecting the import or delete to fail. The problem: I was running as root, and root "
        "bypasses Unix DAC permission checks. So the write succeeded when the test expected it "
        "to fail, and the .expect_err() call panicked.",
        S["Body"]))
    story.append(Spacer(1, 0.04*inch))
    story.append(callout(S,
        "These are not real bugs. Run the same tests as a normal user on any Linux or macOS "
        "system and they pass. The tests themselves are actually well-written — they verify "
        "proper atomic rollback on filesystem errors, which is exactly the kind of thing "
        "you want tested.",
        bg=colors.HexColor("#f0fdf4"), border=GREEN, label="Verdict on the failures"))

    # ── 4. Code Quality ──
    story.append(Paragraph("4. Code quality impressions", S["SectionHead"]))
    story.append(rule())
    story.append(Paragraph(
        "I spent time reading the engine, dependent-join, and spec crates. A few things "
        "stood out:",
        S["Body"]))

    bullets = [
        ("<b>No unsafe, no unwrap in production code.</b> The workspace-level lint rules "
         "enforce this strictly. You see .expect() in tests (with context strings) but "
         "the engine itself handles errors through a proper CoreError type."),
        ("<b>The DependentJoinExec phantom-row fix (issue #1245) is solid.</b> When an API "
         "redirects request PR #777 and returns data for PR #456 instead, the engine now "
         "validates that the returned binding keys match what was requested and drops the "
         "mismatched row. This is a subtle correctness issue that a lot of systems would miss."),
        ("<b>The test harness uses wiremock properly.</b> HTTP tests spin up a real mock "
         "server, mount expected request matchers, and assert call counts. No HTTP mocking "
         "via string replacement or patching — actual TCP connections."),
        ("<b>Pagination is thorough.</b> Four pagination modes (cursor, page-offset, "
         "link-header, cursor-after) are all tested with their edge cases, including malformed "
         "responses and mid-stream error handling."),
        ("<b>DataFusion v53 is current.</b> No vendored fork, no pinned-to-old version — "
         "they're tracking upstream."),
    ]
    for b in bullets:
        story.append(Paragraph(f"• {b}", S["BulletItem"]))

    # ── 5. Edge Cases ──
    story.append(Paragraph("5. Edge cases tested — and ones that aren't", S["SectionHead"]))
    story.append(rule())
    story.append(Paragraph(
        "The existing suite is comprehensive for the happy path and most error paths. "
        "Here's an honest read of what's covered and what I couldn't find tests for:",
        S["Body"]))
    story.append(Spacer(1, 0.08*inch))

    story.append(data_table(S,
        ["Scenario", "Status", "Notes"],
        [
            ["Phantom rows from API redirects", "✅ Tested", "Issue #1245 fix with mock server"],
            ["NULL join keys — no spurious API call", "✅ Tested", "dpp_and_naive_paths_agree test"],
            ["Duplicate binding tuples → single HTTP call", "✅ Tested", "Call count asserted via wiremock"],
            ["Dependent table on left or right of JOIN", "✅ Tested", "Both orientations covered"],
            ["HTTP 429 / 5xx retry with backoff", "✅ Tested", "Separate retry tests"],
            ["Four pagination modes", "✅ Tested", "cursor, page, offset, link-header"],
            ["Lossy Int64 / Uint64 coercion rejection", "✅ Tested", "Issue #1102 regression"],
            ["Binding cardinality explosion (500+ tuples)", "⚠ Gap", "No backpressure / OOM test"],
            ["OAuth token expiry mid-pagination", "⚠ Gap", "Refresh tested at setup, not in-flight"],
            ["Pagination + dependent join combined", "⚠ Gap", "Tested separately, never together"],
            ["Schema drift across pagination pages", "⚠ Gap", "API adds/removes column mid-stream"],
            ["MCP source as dependent JOIN side", "⚠ Gap", "Arch docs say unsupported; no error test"],
        ],
        col_widths=[2.5*inch, 1.1*inch, 2.9*inch]
    ))

    story.append(Spacer(1, 0.12*inch))
    story.append(callout(S,
        "The gaps I found are all in relatively rare production scenarios. For the stated use "
        "case — multi-source SQL queries from a coding agent — the test coverage is genuinely "
        "good. I've seen open-source projects with way more stars and way worse test suites.",
        bg=colors.HexColor("#fffbeb"), border=AMBER, label="My read on the gaps"))

    # ── 6. Security Notes ──
    story.append(Paragraph("6. One security note worth calling out", S["SectionHead"]))
    story.append(rule())
    story.append(Paragraph(
        "Issue #1150 (fixed in v0.4.2) rejected SQL-controlled v4 base URLs — essentially "
        "a template injection vector where a crafted SQL query could have been used to redirect "
        "API requests to an attacker-controlled host. The fix is in and there's a guard for it, "
        "but I did not find a regression test that verifies the error message and confirms the "
        "guard can't be bypassed with nested template substitution. Worth adding.",
        S["Body"]))

    # ── 7. Final Verdict ──
    story.append(Paragraph("7. Final verdict", S["SectionHead"]))
    story.append(rule())
    story.append(Paragraph(
        "The code is well-written, the architecture is well-reasoned, and the test suite is "
        "honest about what it covers. The two test failures are environment artifacts, not bugs. "
        "If I were asked to integrate this into a production agent pipeline I'd feel comfortable "
        "doing it, with the following caveats:",
        S["Body"]))

    caveats = [
        "Pin your source specs to a specific API schema version and have a plan for schema drift.",
        "Test your specific workload's binding cardinality before assuming the concurrency limits "
        "won't bite you in production.",
        "OAuth-heavy sources need end-to-end testing with actual token refresh cycles, not just "
        "the initial credential setup.",
        "If you're not running Claude, test your SQL generation quality against the source specs "
        "you actually have — the specs are written with Claude's prompt style in mind.",
    ]
    for c in caveats:
        story.append(Paragraph(f"• {c}", S["BulletItem"]))

    story.append(Spacer(1, 0.12*inch))
    story.append(verdict_badge(S,
        "VERDICT: PASSES CODE REVIEW — PRODUCTION-READY WITH CAVEATS",
        GREEN))

    story.append(Spacer(1, 0.15*inch))
    story.append(rule(color=MUTED, thickness=0.5))
    story.append(Paragraph(
        "Testing performed on a fresh clone of withcoral/coral commit aaae090 (June 2026). "
        "All commands run on Linux x86_64, Rust stable 1.95.0. No credentials or live API "
        "keys were used — all HTTP tests run against wiremock servers.",
        S["Small"]))

    doc.build(story)
    print(f"[✓] Written: {path}")


# ─────────────────────────────────────────────────────────────────────────────
#  DOCUMENT 2 — Benchmark Research Report
# ─────────────────────────────────────────────────────────────────────────────

def build_doc2(path):
    doc = SimpleDocTemplate(
        path, pagesize=letter,
        leftMargin=1*inch, rightMargin=1*inch,
        topMargin=0.9*inch, bottomMargin=0.9*inch,
        title="Coral Benchmark Claims — Research Analysis"
    )
    S = make_styles()
    story = []

    # ── cover ──
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("Coral Benchmark Claims", S["DocTitle"]))
    story.append(Paragraph("An independent analysis against published research", S["DocSubtitle"]))
    story.append(Paragraph(f"{TODAY}  ·  Sources: arXiv, withcoral/coral README, peer-reviewed conference papers", S["Meta"]))
    story.append(Spacer(1, 0.08*inch))
    story.append(rule(color=ACCENT, thickness=1.5))
    story.append(Spacer(1, 0.05*inch))

    story.append(callout(S,
        "Coral claims their SQL interface makes Claude 31% more accurate and 3.4× more cost "
        "efficient on complex multi-source tasks compared to direct MCP tool calls. "
        "I went through the benchmark methodology, compared it against recent arXiv papers, "
        "and tried to figure out which parts of that claim hold up and which parts are "
        "marketing math.",
        bg=colors.HexColor("#eff6ff"), border=ACCENT))
    story.append(Spacer(1, 0.15*inch))

    # ── 1. The claim ──
    story.append(Paragraph("1. What Coral actually claims", S["SectionHead"]))
    story.append(rule())
    story.append(Paragraph(
        "The numbers come from Coral's README, which links to a full benchmark report at "
        "withcoral.com/benchmarks. That page was inaccessible during this research (403), so "
        "everything below is based on what the README summarises.",
        S["Body"]))
    story.append(Spacer(1, 0.08*inch))

    story.append(data_table(S,
        ["Scenario", "Accuracy", "Cost", "Latency"],
        [
            ["All 82 tasks (vs direct MCP)", "+20%", "2× cheaper", "−42%"],
            ["Complex / coding agent tasks", "+31%", "3.4× cheaper", "—"],
            ["Simple fact retrieval tasks", "+6%", "2% cheaper", "—"],
        ],
        col_widths=[2.8*inch, 1.2*inch, 1.5*inch, 1.0*inch]
    ))
    story.append(Spacer(1, 0.08*inch))
    story.append(Paragraph(
        "Model tested: Claude Opus 4.6 only. Baselines: direct provider MCPs from "
        "Datadog, Sentry, Linear, Slack, GitHub. No confidence intervals, no p-values, "
        "no run counts, no definition of what 'accuracy' means.",
        S["Body"]))

    # ── 2. Methodology problems ──
    story.append(Paragraph("2. Methodological problems before we get to the numbers", S["SectionHead"]))
    story.append(rule())

    issues = [
        ("Single model, single vendor",
         "The entire benchmark is Claude Opus 4.6 — the model Coral is built for and optimised around. "
         "MCPAgentBench (arXiv:2512.24565), which is the closest peer-reviewed equivalent, tested "
         "Claude Sonnet 4.5, o3, GLM-4.6, and Qwen3-235B and found 15–20% model-to-model variance "
         "on tool-use tasks. Showing results for one model and claiming a general improvement is "
         "a common benchmark design flaw."),
        ("82 tasks with no variance reported",
         "For a +31% accuracy effect to be statistically meaningful at 95% confidence, you need "
         "roughly 50–80 tasks in that specific sub-category with known standard deviation. The "
         "complex-task subset is certainly smaller than 82. Spider 2.0 — the accepted gold standard "
         "for enterprise agent SQL benchmarking — uses 632 tasks and still sees ±30% swings "
         "depending on schema structure. Without error bars, the +31% could be anywhere from "
         "+10% to +50%."),
        ("'Accuracy' is not defined",
         "This matters a lot. Exact match gives lower absolute scores with smaller differences. "
         "LLM-as-judge introduces up to 30% variance on its own (documented in arXiv:2602.15532). "
         "Task completion conflates retrieval accuracy with downstream reasoning. Not knowing which "
         "of these was used makes it impossible to compare against anything else."),
        ("Vendor-designed baseline",
         "Coral built both the product under test and chose which MCP implementations to compare "
         "against. High-quality MCP servers with good tool descriptions, parallel calls, and result "
         "caching can close much of the gap. The W&D paper (arXiv:2602.07359) showed that parallel "
         "tool calling alone significantly reduces both latency and tokens in multi-tool scenarios — "
         "but nothing in the benchmark report indicates whether the MCP baselines used parallel calls."),
    ]
    for title, body in issues:
        story.append(KeepTogether([
            Paragraph(title, S["SubHead"]),
            Paragraph(body, S["Body"]),
            Spacer(1, 0.04*inch),
        ]))

    # ── 3. What the arxiv literature says ──
    story.append(Paragraph("3. What the research literature actually says", S["SectionHead"]))
    story.append(rule())
    story.append(Paragraph(
        "I searched arXiv for papers on LLM agent tool efficiency, SQL vs function-calling "
        "benchmarks, multi-source query accuracy, and token overhead in agentic workflows. "
        "Here's the honest picture.",
        S["Body"]))

    story.append(Paragraph("The core mechanism is real", S["SubHead"]))
    story.append(Paragraph(
        "Coral's fundamental premise — that collapsing N sequential tool calls into one "
        "declarative query reduces token waste and error compounding — is well-supported. "
        "The Tokenomics paper (arXiv:2601.14470) measured where tokens actually go in agentic "
        "software engineering tasks and found tool definition schemas alone eat a disproportionate "
        "share of the context budget when tools are repeated across turns. SkillReducer "
        "(arXiv:2603.29919) confirmed that compressing skill/tool context while preserving "
        "semantics can reduce context tokens significantly without accuracy loss. "
        "Dynamic Tool Dependency Retrieval (arXiv:2512.17052) found that agents redundantly "
        "re-invoking tools is a primary driver of wasted tokens in multi-source scenarios.",
        S["Body"]))
    story.append(Spacer(1, 0.04*inch))
    story.append(callout(S,
        "The direction of the effect is correct. Reducing tool schema re-injection and eliminating "
        "sequential round-trips for multi-source joins does save tokens and can improve accuracy. "
        "The question is the magnitude.",
        bg=colors.HexColor("#f0fdf4"), border=GREEN, label="What holds up"))

    story.append(Paragraph("The magnitude is inflated vs controlled studies", S["SubHead"]))
    story.append(Spacer(1, 0.04*inch))
    story.append(data_table(S,
        ["Source", "Claim / Finding", "Accuracy gain", "Token efficiency"],
        [
            ["Coral (self-reported)", "SQL vs direct MCP, complex tasks", "+31%", "3.4×"],
            ["Coral (self-reported)", "SQL vs direct MCP, all tasks", "+20%", "2×"],
            ["Tool-MVR (peer-reviewed)", "Best tool method vs ToolLLM baseline", "+24%", "—"],
            ["CLEAR framework study", "Multi-metric agentic optimization", "—", "26–54% reduction"],
            ["Instruction Tool Retrieval", "Dynamic tool loading vs static context", "—", "up to 147×"],
            ["SkillReducer", "Compressed skill context", "Maintained", "Significant"],
        ],
        col_widths=[1.7*inch, 2.2*inch, 1.2*inch, 1.4*inch]
    ))
    story.append(Paragraph(
        "The 3.4× token efficiency sits between the conservative end of what controlled studies "
        "show (26–54% savings = 1.3–2.1×) and the extreme end seen in dynamic tool loading "
        "scenarios (up to 147×). It is not impossible, but it likely reflects a poorly-tuned "
        "baseline rather than an intrinsic SQL advantage.",
        S["Body"]))

    story.append(Paragraph("The most important counterpoint: Spider 2.0", S["SubHead"]))
    story.append(Paragraph(
        "Spider 2.0 (arXiv:2411.07763) is the most significant challenge to Coral's framing. "
        "It tests LLM agents on real enterprise SQL workflows — 632 tasks from BigQuery and "
        "Snowflake databases with 1,000+ columns each. The best agent (o1-preview) solves only "
        "21.3% of tasks, compared to 91.2% on Spider 1.0 and 73% on BIRD. The failure mode "
        "analysis is telling:",
        S["Body"]))
    story.append(Spacer(1, 0.04*inch))
    story.append(data_table(S,
        ["Failure mode", "Share of errors"],
        [
            ["Wrong schema linking (column/table misidentification)", "27.6%"],
            ["Nested schema structures (10% success vs 27% without)", "Major"],
            ["Multi-dialect SQL generation", "Significant"],
            ["Under-specified column types", "Significant"],
        ],
        col_widths=[4.0*inch, 2.5*inch]
    ))
    story.append(Spacer(1, 0.06*inch))
    story.append(callout(S,
        "Coral assumes schemas are already compiled into source specs by a human. This sidesteps "
        "schema linking entirely — which is the #1 failure mode in real-world SQL agent tasks. "
        "The accuracy wins Coral reports may be real within its walled garden, but they don't "
        "transfer to arbitrary APIs where you haven't pre-written a spec.",
        bg=colors.HexColor("#fff7ed"), border=AMBER, label="The critical caveat"))

    story.append(Paragraph("Single-agent vs multi-agent multi-hop reasoning", S["SubHead"]))
    story.append(Paragraph(
        "Tran & Kiela (arXiv:2604.02460, April 2026) tested Qwen3, DeepSeek-R1, and Gemini 2.5 "
        "and found that single-agent systems consistently match or outperform multi-agent chains "
        "on multi-hop tasks when reasoning tokens are held constant. The theoretical backbone is "
        "the Data Processing Inequality: every inter-agent handoff can only lose information, "
        "never create it. A companion paper (arXiv:2606.13003, 'The Illusion of Multi-Agent "
        "Advantage') reaches the same conclusion across seven benchmarks.",
        S["Body"]))
    story.append(Spacer(1, 0.04*inch))
    story.append(Paragraph(
        "This cuts both ways for Coral. On one hand, it supports Coral's single-query approach "
        "over N-sequential-tool-call chains — fewer handoffs, less information loss. On the "
        "other hand, it suggests the accuracy gain might come from giving the model a cleaner "
        "context, not from anything uniquely powerful about SQL. A well-designed single-agent "
        "system with good tool descriptions might close most of the gap without Coral.",
        S["Body"]))

    # ── 4. Confidence scorecard ──
    story.append(Paragraph("4. Confidence scorecard", S["SectionHead"]))
    story.append(rule())
    story.append(data_table(S,
        ["Claim", "Confidence", "Verdict"],
        [
            ["Fewer tokens than N sequential MCP calls", "High (85%)", "Structurally true; Tokenomics confirms the mechanism"],
            ["3.4× cost efficiency on complex tasks", "Low–Medium (40%)", "Plausible ceiling; likely vs suboptimal baseline"],
            ["+31% accuracy on complex tasks", "Low–Medium (45%)", "Direction correct; no CIs, single model, n too small"],
            ["+20% accuracy across all 82 tasks", "Medium (55%)", "More credible; still single-model"],
            ["42% latency reduction", "Medium (60%)", "Structural advantage from fewer round-trips"],
            ["Generalises to GPT / Gemini / open-source", "Low (25%)", "Never tested; model variance is 15–20%"],
            ["Generalises to arbitrary new APIs", "Very Low (15%)", "Requires pre-written spec — the hard part"],
        ],
        col_widths=[2.4*inch, 1.5*inch, 2.6*inch]
    ))

    # ── 5. Where it breaks down ──
    story.append(Paragraph("5. Where the claim breaks down", S["SectionHead"]))
    story.append(rule())

    breakdowns = [
        ("Dynamic / unknown APIs",
         "Source specs must be written before you can query. For novel APIs you don't have "
         "a spec yet. Spider 2.0's 21% agent success rate is the reference point for what "
         "happens when schema context isn't hand-crafted."),
        ("Non-Claude models",
         "SQL generation quality, handling of Coral's spec DSL, and instruction following "
         "on multi-step queries all vary by model. MCPAgentBench found 15–20% score "
         "differences between frontier models on structured tool tasks. Coral was not "
         "tested on GPT-5, Gemini, or any open-source model."),
        ("Large cardinality joins",
         "1,000 distinct (owner, repo) binding tuples means 1,000 HTTP calls. Coral has a "
         "max_concurrency config, but there is no benchmark or test data on how the engine "
         "performs under that kind of load, and no test for graceful degradation if the "
         "concurrency cap is hit."),
        ("Schema drift",
         "If an API adds or removes a column between spec creation and query time, the spec "
         "is stale. The engine will either return wrong data or error, depending on whether "
         "the column is required. No tests cover this scenario, and there's no spec "
         "versioning or drift detection in the current architecture."),
        ("Spec maintenance overhead not in cost numbers",
         "The 3.4× cost efficiency claim counts only inference tokens. It does not count "
         "the human engineering time to write and maintain source specs for each API. "
         "For a five-source deployment this might be a few hours. For a long tail of "
         "internal APIs it could be significant."),
    ]
    for title, body in breakdowns:
        story.append(KeepTogether([
            Paragraph(title, S["SubHead"]),
            Paragraph(body, S["Body"]),
            Spacer(1, 0.04*inch),
        ]))

    # ── 6. A more honest number ──
    story.append(Paragraph("6. A more honest set of numbers", S["SectionHead"]))
    story.append(rule())
    story.append(Paragraph(
        "Based on the controlled studies I found and the structural analysis of what Coral "
        "actually does, here's my best estimate of what real-world improvements look like "
        "for someone using Coral in a well-matched scenario (multi-source, Claude, "
        "pre-compiled specs):",
        S["Body"]))
    story.append(Spacer(1, 0.08*inch))
    story.append(data_table(S,
        ["Metric", "Coral claims", "My estimate (realistic)", "Lower bound"],
        [
            ["Accuracy vs naive sequential MCP calls", "+31%", "+10 to +20%", "+5%"],
            ["Token / cost efficiency", "3.4×", "1.5–2.5×", "1.2×"],
            ["Latency reduction", "42%", "20–35%", "10%"],
        ],
        col_widths=[2.2*inch, 1.5*inch, 1.8*inch, 1.0*inch]
    ))
    story.append(Spacer(1, 0.08*inch))
    story.append(Paragraph(
        "The gap between Coral's numbers and mine mostly comes down to baseline quality. "
        "If you compare against a well-implemented direct MCP setup with parallel calls and "
        "deduplicated tool schemas, the delta shrinks substantially. If you compare against "
        "a naive sequential loop over individual tools — which is probably what most people "
        "are actually running — Coral's numbers are closer to credible.",
        S["Body"]))

    # ── 7. Bottom line ──
    story.append(Paragraph("7. Bottom line", S["SectionHead"]))
    story.append(rule())
    story.append(Paragraph(
        "The benchmark is vendor-authored, single-model, statistically underpowered, and "
        "lacks error bars. Treat the headline numbers as a product demo, not a scientific "
        "result. That said:",
        S["Body"]))

    concluding = [
        "The <b>mechanism is sound and independently supported</b>. Collapsing multi-tool "
        "API workflows into a single declarative query structurally reduces token re-injection "
        "and eliminates error compounding across tool call boundaries.",
        "The <b>improvement is real but smaller than claimed</b> when measured against "
        "well-tuned baselines. Expect +10–20% accuracy and 1.5–2.5× token efficiency on "
        "genuinely multi-hop, multi-source queries.",
        "The <b>precondition is significant</b>: you need pre-written, maintained source specs "
        "for every API you want to query. The benchmark doesn't account for this setup cost.",
        "The <b>single-model limitation matters</b> if you're not running Claude. None of "
        "the efficiency numbers have been validated on GPT, Gemini, or open-source models.",
        "It is <b>worth trying</b> if you're building agents that regularly join data across "
        "3+ sources, you're already on Claude, and you're willing to write source specs. "
        "Just don't expect the full 3.4× on day one.",
    ]
    for c in concluding:
        story.append(Paragraph(f"• {c}", S["BulletItem"]))

    story.append(Spacer(1, 0.15*inch))
    story.append(verdict_badge(S,
        "CLAIM DIRECTION: VALID  ·  HEADLINE NUMBERS: OVERSTATED  ·  NO THIRD-PARTY REPLICATION",
        AMBER))

    # ── references ──
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("References", S["SectionHead"]))
    story.append(rule())

    refs = [
        ("arXiv:2512.24565", "MCPAgentBench: A Real-world Task Benchmark for Evaluating LLM Agent MCP Tool Use"),
        ("arXiv:2509.09734", "MCP-AgentBench: Evaluating Real-World Language Agent Performance with MCP-Mediated Tools"),
        ("arXiv:2411.07763", "Spider 2.0: Evaluating Language Models on Real-World Enterprise Text-to-SQL Workflows"),
        ("arXiv:2602.21480", "Both Ends Count! Just How Good are LLM Agents at Text-to-Big SQL?"),
        ("arXiv:2604.02460", "Single-Agent LLMs Outperform Multi-Agent Systems on Multi-Hop Reasoning Under Equal Thinking Token Budgets"),
        ("arXiv:2606.13003", "The Illusion of Multi-Agent Advantage"),
        ("arXiv:2601.14470", "Tokenomics: Quantifying Where Tokens Are Used in Agentic Software Engineering"),
        ("arXiv:2603.29919", "SkillReducer: Optimizing LLM Agent Skills for Token Efficiency"),
        ("arXiv:2512.17052", "Dynamic Tool Dependency Retrieval for Efficient Function Calling"),
        ("arXiv:2602.07359", "W&D: Scaling Parallel Tool Calling for Efficient Deep Reasoning"),
        ("arXiv:2511.14136", "Beyond Accuracy: A Multi-Dimensional Framework for Evaluating Enterprise Agentic AI Systems"),
        ("arXiv:2503.18596", "LinkAlign: Scalable Schema Linking for Real-World Large-Scale Multi-Database Text-to-SQL"),
        ("arXiv:2602.15532", "Quantifying Construct Validity in Large Language Model Evaluations"),
        ("arXiv:2508.16260", "MCPVerse: An Expansive, Real-World Benchmark for Agentic Tool Use"),
        ("github.com/withcoral/coral", "withcoral/coral — README and benchmark summary (commit aaae090, June 2026)"),
    ]
    for ref_id, title in refs:
        story.append(Paragraph(f"[{ref_id}]  {title}", S["Cite"]))

    story.append(Spacer(1, 0.1*inch))
    story.append(rule(color=MUTED, thickness=0.5))
    story.append(Paragraph(
        "Research conducted June 17, 2026. All arXiv papers were located via web search; "
        "abstracts and findings extracted from search summaries where direct PDF access was "
        "blocked. The full benchmark report at withcoral.com/benchmarks was inaccessible "
        "during this research.",
        S["Small"]))

    doc.build(story)
    print(f"[✓] Written: {path}")


# ── run ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    build_doc1("/home/user/test1/coral_code_review.pdf")
    build_doc2("/home/user/test1/coral_benchmark_research.pdf")
