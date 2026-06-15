import type { Plugin } from '@envelop/core';
import { Logger } from '../logger';
import { ContextType } from '../types';

export const useLogger = (): Plugin<ContextType> => {
  return {
    // run after buildHeaders so requestId and client are already on the context
    onExecute({ args, extendContext }) {
      const ctx = args.contextValue as ContextType;
      const logger = new Logger();
      logger.setRequestId(ctx.requestId);
      logger.setClient(ctx.client);
      extendContext({ logger } as any);
    },
  };
};
