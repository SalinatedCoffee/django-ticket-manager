// Backend interaction

const ENDPOINT_URI = "http://localhost:8000/api/";

export const TktEntType = {
  // enum for usertypes
  User: Symbol("tktuser"),
  Agent: Symbol("tktagent"),
  Admin: Symbol("tktadmin")
};

export async function register() {
  // this should create a new tktuser account given json as input
  // return true and valid json obj on success
  // other entity types are currently unsupported by endpoint
  return;
};

export async function login() {
  // this should log a user in given json as input
  // return true on success
  return;
};

export async function logout() {
  // this should log a user out
  // return true on success
  return;
};

export async function entityDetails() {
  // this should fetch user details given username
  // return valid json on success with tkt-entity type embedded
  return;
};

export async function eventDetails() {
  // this should fetch event details given uuid
  // return valid json on success (including uuid)
  return;
};

export async function eventList() {
  // this should fetch list of all events
  // return valid json on success
  // {ev details}, {ev details}, ...
  return;
};

export async function eventRegisteredEntityList() {
  // this should fetch list of all entities enrolled to event given uuid
  // return valid json on success
  return;
};

export async function createNewEvent() {
  // this should create new event given json
  // return true, valid json on success
  return;
};

// Utility functions

export async function fetchFromBe() {
  // this should wrap fetch() given same params
  // prepend uri prefix and set csrf header
  // return promise
  // TODO: consider adding checks on server response to determine if user
  // should be redirected to login page
  return;
};

export function grabCsrf() {
  // this should set a csrf cookie from endpoint
  // return true on success
  return;
};

export function saveTotpSecret() {
  // this should save totp to safe local storage given event uuid
  // return true on success
  return;
};

export function getTotpSecret() {
  // this should retrieve totp from local storage
  // return totp on success, false otherwise
  return;
};