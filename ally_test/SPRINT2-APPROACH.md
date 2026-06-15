# Sprint 2 Approach — NASA NEO Feed via GraphQL Mesh v0

## What was implemented

### .meshrc.yml

Configured a `jsonSchema` source pointing at the NASA NEO Feed endpoint. The handler uses `responseSchema` (a local sample JSON file) to infer types during codegen, so a real network call isn't needed at build time.

```yaml
sources:
  - name: NasaNEO
    handler:
      jsonSchema:
        endpoint: "https://api.nasa.gov/neo/rest/v1/feed"
        operations:
          - type: Query
            field: nasaNeoFeed
            path: "?start_date={args.startDate}&end_date={args.endDate}&api_key=DEMO_KEY"
            method: GET
            argTypeMap:
              startDate: String
              endDate: String
            responseSchema: ./data/nasa-neo-sample.json
```

`data/nasa-neo-sample.json` is a trimmed copy of a real NASA response covering two dates. Mesh uses it to infer the raw GraphQL types — particularly the nested `near_earth_objects`, `estimated_diameter`, and `close_approach_data` structures.

### GraphQL schema exposed to consumers

Only the fields listed in the ticket are exposed (`src/schema/neo/neo.graphql`). Everything else from the NASA payload (links, orbital data, sentry objects, etc.) is deliberately excluded:

```graphql
type NearEarthObjectFeed {
  elementCount: Int
  objects: [NearEarthObject]
}

type NearEarthObject {
  id: String
  name: String
  isPotentiallyHazardousAsteroid: Boolean
  estimatedDiameterMinKm: Float
  estimatedDiameterMaxKm: Float
  closeApproachDate: String
  relativeVelocityKph: String
  missDistanceKm: String
}
```

The `nearEarthObjects(startDate, endDate)` query is added to the root `Query` type in `schema.graphql`.

### Resolver (`src/schema/neo/neo.ts`)

The resolver:
1. Gets the Mesh SDK via `getMesh` + `findAndParseConfig` — initialised once and cached.
2. Calls `sdk.nasaNeoFeed(...)` — the SDK handles building the URL and fetching.
3. Does **not** make the HTTP call directly.
4. Flattens `near_earth_objects` (which is a `Record<date, Neo[]>`) into a plain array using `Object.values(...).flat()` — this lives in the resolver layer, not inside Mesh.
5. Maps raw snake_case fields to the camelCase shape the schema expects.

### Why the flatten is in the resolver, not a Mesh transform

Mesh transforms (like `rename` or `filterSchema`) operate on field names and types — they can't restructure a dynamic date-keyed object into an array. That kind of logic belongs in the resolver where you have full control over the shape.

### Caching consideration

`DEMO_KEY` is rate-limited (~30 req/hour). A simple improvement would be to add `@envelop/response-cache` (already installed as a dependency) with a TTL of a few minutes, since the NEO data for a given date range doesn't change.

## What would need to happen in a real environment

- `npx mesh generate-sdk` would need to run (or happen in CI) to produce a typed SDK under `.mesh/`. This requires network access to fetch the NASA response for schema introspection if no `responseSchema` file is provided.
- The `responseSchema` approach used here avoids that — the sample JSON covers the full structure so codegen works offline.
- In tests, the Mesh SDK call is mocked so no network is needed.

## Trade-offs

| Choice | Reason |
|---|---|
| Local sample JSON for schema inference | Avoids network dependency at build time; sample covers all relevant fields |
| Flatten in resolver, not Mesh transform | Mesh transforms can't restructure dynamic keys; resolver is the right layer |
| Singleton SDK promise | Mesh initialisation is expensive; one instance is shared across requests |
| `DEMO_KEY` hardcoded | Required by the ticket; in production this would come from an env var |
