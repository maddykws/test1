import type { Config } from '@jest/types';

// Sync object
const config: Config.InitialOptions = {
  verbose: true,
  transform: {
    '^.+\\.ts?$': 'ts-jest',
  },
  testTimeout: 30000,
  // run test files one at a time so saveAddress tests don't corrupt addresses.json
  // for other test suites running in parallel
  runInBand: true,
};
export default config;
