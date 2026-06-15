import { parse } from 'graphql';
import { executor } from '../exectuor';
import fs from 'fs';
import path from 'path';

const dataPath = path.join(__dirname, '../../data/addresses.json');

let originalData: string;
beforeAll(() => {
  originalData = fs.readFileSync(dataPath, 'utf-8');
});
// restore before each test so mutations from one test don't bleed into the next
beforeEach(() => {
  fs.writeFileSync(dataPath, originalData);
});
afterAll(() => {
  fs.writeFileSync(dataPath, originalData);
});

describe('saveAddress', () => {
  test('creates a new address entry', async () => {
    const mutation = `
      mutation SaveAddress(
        $username: String!
        $street: String!
        $city: String!
        $state: String!
        $zipcode: String!
      ) {
        saveAddress(username: $username, street: $street, city: $city, state: $state, zipcode: $zipcode) {
          street
          city
          state
          zipcode
        }
      }
    `;

    const result = await executor({
      document: parse(mutation),
      variables: {
        username: 'testuser',
        street: '999 New Ave',
        city: 'Columbus',
        state: 'OH',
        zipcode: '43201',
      },
    });

    expect(result).toEqual({
      data: {
        saveAddress: {
          street: '999 New Ave',
          city: 'Columbus',
          state: 'OH',
          zipcode: '43201',
        },
      },
      metadata: expect.objectContaining({ requestId: expect.any(String) }),
    });
  });

  test('does not overwrite existing records', async () => {
    const mutation = `
      mutation SaveAddress(
        $username: String!
        $street: String!
        $city: String!
        $state: String!
        $zipcode: String!
      ) {
        saveAddress(username: $username, street: $street, city: $city, state: $state, zipcode: $zipcode) {
          street
          city
          state
          zipcode
        }
      }
    `;

    // save a new user
    await executor({
      document: parse(mutation),
      variables: {
        username: 'newguy',
        street: '1 First St',
        city: 'Newark',
        state: 'OH',
        zipcode: '43055',
      },
    });

    // confirm jack still exists after the save
    const data = JSON.parse(fs.readFileSync(dataPath, 'utf-8'));
    expect(data['jack']).toBeDefined();
    expect(data['jack'].street).toBe('123 Street St.');
    expect(data['newguy']).toBeDefined();
  });
});
