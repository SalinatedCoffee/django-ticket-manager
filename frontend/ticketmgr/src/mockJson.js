// Various JSON objects for use in mock testing.

export const MOCK_USR_REG = JSON.parse(`
  {
    "username": "MockUser1",
    "password": "MockUserPass",
    "email": "MockUser@domain.com",
    "first_name": "John",
    "last_name": "Mock"
  }`);

export const MOCK_EV_LIST = JSON.parse(`
  [
    {
      "title": "Event0",
      "description": "This is event 0.",
      "datetime": "2022-12-01T08:12:46.787312Z",
      "uuid": "7bf953d0-bce0-4d26-9bf8-957eb0dc071a"
    },
    {
      "title": "Event1",
      "description": "This is event 1.",
      "datetime": "2022-12-01T08:12:46.793435Z",
      "uuid": "24d49959-9b14-4c87-845d-e74001e759e2"
    },
    {
      "title": "Event2",
      "description": "This is event 2.",
      "datetime": "2022-12-01T08:12:46.804278Z",
      "uuid": "eae0106f-7957-4f06-a0b8-75032af3b390"
    }
  ]`);

export const MOCK_USR_LIST = JSON.parse(`
  [
    {
      "user": {
        "username": "user1",
        "first_name": "John1",
        "last_name": "Doe1",
        "email": "johndoe1@domain.com"
      },
      "uuid": "38e8a5f1-6e66-416b-adcb-86bee9561d33",
      "event_count": 0
    },
    {
      "user": {
        "username": "user2",
        "first_name": "John2",
        "last_name": "Doe2",
        "email": "johndoe2@domain.com"
      },
      "uuid": "38e8a5f1-6e66-416b-adcb-86bee9561d34",
      "event_count": 1
    },
    {
      "user": {
        "username": "user3",
        "first_name": "John3",
        "last_name": "Doe3",
        "email": "johndoe3@domain.com"
      },
      "uuid": "38e8a5f1-6e66-416b-adcb-86bee9561d35",
      "event_count": 99
    }
  ]`);

export const MOCK_AGT_LIST = JSON.parse(`
  [
    {
      "agent": {
        "username": "agent0",
        "first_name": "Jane0",
        "last_name": "Doe0",
        "email": "agent0@domain.com"
      },
      "agent": {
        "username": "agent1",
        "first_name": "Jane1",
        "last_name": "Doe1",
        "email": "agent1@domain.com"
      },
      "agent": {
        "username": "agent2",
        "first_name": "Jane2",
        "last_name": "Doe2",
        "email": "agent2@domain.com"
      }
    }
  ]`);

export const MOCK_AMN_LIST = JSON.parse(`
  [
    {
      "admin": {
        "username": "admin0",
        "first_name": "Admin0",
        "last_name": "lname0",
        "email": "admin0@domain.com"
      },
      "event_count": 1
    },
    {
      "admin": {
        "username": "admin1",
        "first_name": "Admin1",
        "last_name": "lname1",
        "email": "admin1@domain.com"
      },
      "event_count": 1
    }
  ]`);

export const MOCK_USR_DETAIL = JSON.parse(`
  {
    "user": {
      "username": "user1",
      "first_name": "John1",
      "last_name": "Doe1",
      "email": "johndoe1@domain.com"
    },
    "uuid": "38e8a5f1-6e66-416b-adcb-86bee9561d33",
    "event_count": 0
  }`);

export const MOCK_AGT_DETAIL = JSON.parse(`
  {
    "agent": {
      "username": "agent0",
      "first_name": "Jane0",
      "last_name": "Doe0",
      "email": "agent0@domain.com"
    }
  }`);

export const MOCK_AMN_DETAIL = JSON.parse(`
  {
    "admin": {
      "username": "admin0",
      "first_name": "Admin0",
      "last_name": "lname0",
      "email": "admin0@domain.com"
    },
    "event_count": 1
  }`);

export const MOCK_EV_REG = JSON.parse(`
  {
    "title": "Event0",
    "description": "This is event 0.",
    "datetime" :"2022-12-01T08:12:46.787312Z"
  }`);

export const MOCK_EV_DETAIL = JSON.parse(`
  {
    "title": "Event0",
    "description": "This is event 0.",
    "datetime" :"2022-12-01T08:12:46.787312Z",
    "uuid":"7bf953d0-bce0-4d26-9bf8-957eb0dc071a"
  }`);
