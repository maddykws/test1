export type Address = {
  street: string;
  city: string;
  state: string;
  zipcode: string;
};

export type Addresses = {
  [key: string]: Address;
};

export type Args = {
  username: string;
};

export type SaveAddressArgs = {
  username: string;
  street: string;
  city: string;
  state: string;
  zipcode: string;
};
