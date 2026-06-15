import fs from 'fs';
import path from 'path';
import { Addresses, Address, Args, SaveAddressArgs } from './types';
import { GraphQLError } from 'graphql';

const dataPath = path.join(__dirname, '../../../data/addresses.json');

const readAddresses = (): Addresses => {
  const raw = fs.readFileSync(dataPath, 'utf-8');
  return JSON.parse(raw) as Addresses;
};

const _getAddress = (username: string): Address | null => {
  const addresses = readAddresses();
  return addresses[username] ?? null;
};

export const getAddress = (_: any, args: Args, context: any): Address => {
  context.logger.info('getAddress', 'Enter resolver');
  const address = _getAddress(args.username);
  if (address) {
    context.logger.info('getAddress', 'Returning address');
    return address;
  }
  context.logger.error('getAddress', 'No address found');
  throw new GraphQLError('No address found in getAddress resolver');
};

export const saveAddress = (_: any, args: SaveAddressArgs, context: any): Address => {
  context.logger.info('saveAddress', 'Enter resolver');
  const addresses = readAddresses();
  const entry: Address = {
    street: args.street,
    city: args.city,
    state: args.state,
    zipcode: args.zipcode,
  };
  addresses[args.username] = entry;
  fs.writeFileSync(dataPath, JSON.stringify(addresses, null, 2));
  context.logger.info('saveAddress', 'Address saved');
  return entry;
};
