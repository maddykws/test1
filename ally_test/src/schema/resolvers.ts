import { getAddress, saveAddress } from "./address/address";
import { Address, Args, SaveAddressArgs } from "./address/types";
import { getNearEarthObjects } from "./neo/neo";

export const resolvers = {
  Query: {
    address: (parent: any, args: Args, context: any, info: any): Address => {
      return getAddress(parent, args, context);
    },
    nearEarthObjects: (parent: any, args: any, context: any, info: any) => {
      return getNearEarthObjects(parent, args, context);
    },
  },
  Mutation: {
    saveAddress: (parent: any, args: SaveAddressArgs, context: any, info: any): Address => {
      return saveAddress(parent, args, context);
    },
  },
};
