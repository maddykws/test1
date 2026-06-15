import { createYoga } from 'graphql-yoga';
import { buildHTTPExecutor } from '@graphql-tools/executor-http';
import { genSchema } from '../src/schema';
import plugins from '../src/envelop/index';

console.profile = jest.fn();
const schema = genSchema();

const yoga = createYoga({ schema, plugins });

// default executor sends a 'test-client' header so header validation passes
export const executor = buildHTTPExecutor({
  fetch: yoga.fetch,
  headers: { client: 'test-client' },
});

// lets individual tests override headers as needed
export const makeExecutor = (headers: Record<string, string> = {}) =>
  buildHTTPExecutor({
    fetch: yoga.fetch,
    headers,
  });
