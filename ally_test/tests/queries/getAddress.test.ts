import { parse } from 'graphql';
import { executor } from '../exectuor';

describe('getAddress', () => {
  test('Success', async () => {
    const query = `
      query GetAddress($username: String!) {
        address(username: $username) {
          street
          city
          state
          zipcode
        }
      }
    `;

    const result = await executor({
      document: parse(query),
      variables: { username: 'jack' },
    });

    expect(result).toEqual({
      data: {
        address: {
          street: '123 Street St.',
          city: 'Sometown',
          state: 'OH',
          zipcode: '43215',
        },
      },
      metadata: expect.objectContaining({ requestId: expect.any(String) }),
    });
  });

  test('Error', async () => {
    const query = `
      query GetAddress($username: String!) {
        address(username: $username) {
          street
          city
          state
          zipcode
        }
      }
    `;

    const result = await executor({
      document: parse(query),
      variables: { username: 'john' },
    });

    expect(result).toEqual(
      expect.objectContaining({
        errors: expect.arrayContaining([
          expect.objectContaining({
            message: 'No address found in getAddress resolver',
          }),
        ]),
      })
    );
  });
});
