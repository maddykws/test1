import { parse } from 'graphql';
import { makeExecutor } from '../exectuor';

const GET_ADDRESS = `
  query GetAddress($username: String!) {
    address(username: $username) {
      street
      city
      state
      zipcode
    }
  }
`;

const SAVE_ADDRESS = `
  mutation SaveAddress(
    $username: String!
    $street: String!
    $city: String!
    $state: String!
    $zipcode: String!
  ) {
    saveAddress(username: $username, street: $street, city: $city, state: $state, zipcode: $zipcode) {
      street
    }
  }
`;

describe('client header validation', () => {
  test('rejects request with no client header', async () => {
    const exec = makeExecutor({});
    const result = await exec({
      document: parse(GET_ADDRESS),
      variables: { username: 'jack' },
    });
    expect(result).toEqual(
      expect.objectContaining({
        errors: expect.arrayContaining([
          expect.objectContaining({ message: 'Missing required header: client' }),
        ]),
      })
    );
  });

  test('allows query with valid client header', async () => {
    const exec = makeExecutor({ client: 'some-client' });
    const result = await exec({
      document: parse(GET_ADDRESS),
      variables: { username: 'jack' },
    });
    expect(result).toMatchObject({
      data: { address: expect.objectContaining({ street: '123 Street St.' }) },
    });
  });

  test('strata client can run queries', async () => {
    const exec = makeExecutor({ client: 'strata' });
    const result = await exec({
      document: parse(GET_ADDRESS),
      variables: { username: 'jack' },
    });
    expect(result).toMatchObject({
      data: { address: expect.objectContaining({ street: '123 Street St.' }) },
    });
  });

  test('strata client cannot run mutations', async () => {
    const exec = makeExecutor({ client: 'strata' });
    const result = await exec({
      document: parse(SAVE_ADDRESS),
      variables: {
        username: 'strata-user',
        street: '1 St',
        city: 'City',
        state: 'OH',
        zipcode: '00000',
      },
    });
    expect(result).toEqual(
      expect.objectContaining({
        errors: expect.arrayContaining([
          expect.objectContaining({ message: 'strata client is not allowed to perform mutations' }),
        ]),
      })
    );
  });
});
