import type { Plugin } from '@envelop/core';
import { handleStreamOrSingleExecutionResult } from '@envelop/core';
import { v4 as uuid } from 'uuid';
import { GraphQLError, OperationDefinitionNode } from 'graphql';
import { ContextType } from '../types';

export const buildHeaders = (): Plugin<ContextType> => {
  return {
    // ticket 4 fix: generate requestId early so it's in context before onParse / onExecute
    onContextBuilding({ extendContext }) {
      extendContext({ requestId: uuid() } as any);
    },

    onExecute({ args, extendContext }) {
      const request = (args.contextValue as any).request as Request;
      const clientHeader = request?.headers?.get('client') ?? '';

      // ticket 3: every request must send the client header
      if (!clientHeader) {
        throw new GraphQLError('Missing required header: client');
      }

      // ticket 3: strata is read-only — block mutations
      if (clientHeader === 'strata') {
        const op = args.document.definitions.find(
          (d: any): d is OperationDefinitionNode => d.kind === 'OperationDefinition'
        );
        if (op?.operation === 'mutation') {
          throw new GraphQLError('strata client is not allowed to perform mutations');
        }
      }

      // ticket 5: store client so the logger can attach it to every line
      extendContext({ client: clientHeader } as any);

      // ticket 6: append requestId to the response under a `metadata` key
      return {
        onExecuteDone(payload) {
          return handleStreamOrSingleExecutionResult(payload, ({ result, setResult }) => {
            const requestId = (args.contextValue as any).requestId;
            setResult({ ...result, metadata: { requestId } } as any);
          });
        },
      };
    },
  };
};
