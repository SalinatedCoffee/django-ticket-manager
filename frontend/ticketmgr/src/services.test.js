import * as mockJson from './mockJson';
import * as services from './services';

const HTTP_STATUS = (code) => { return {status: code} }

describe('backend interaction services', () => {
  beforeEach(() => {
    fetch.resetMocks();
  });

  test.skip('new user registration', async () => {
    // Should return [true, <TktUser JSON>] on success
    fetch.mockResponseOnce(mockJson.MOCK_USR_DETAIL, HTTP_STATUS(201));
    await services.register(mockJson.MOCK_USR_REG)
      .then(ret => {
        expect(ret[0]).toEqual(true);
        expect(ret[1].uuid).toEqual(mockJson.MOCK_USR_DETAIL.uuid);
        expect(ret[1].user.username)
          .toEqual(mockJson.MOCK_USR_DETAIL.user.username);
      });
    
    // Should return [false, <Error JSON>] on failure w/ malformed payload
    fetch.mockResponseOnce({message: 'fail'}, HTTP_STATUS(400));
    await services.register(mockJson.MOCK_USR_REG)
      .then(ret => {
        expect(ret[0]).toEqual(false);
        expect(ret[1].message).toEqual('fail');
      });

    // Should return [false, null] on miscellaneous failures
    fetch.mockResponseOnce({}, HTTP_STATUS(500));
    await services.register(mockJson.MOCK_USR_REG)
      .then(ret => {
        expect(ret[0]).toEqual(false);
        expect(ret[1]).toEqual(null);
      });
  });

  test.skip('entity login', async () => {
    const MOCK_CRED = {username: 'username', password: 'password'}
    // Should return [services.TktEntType.<enum>, <Response JSON>] on success
    fetch.mockResponseOnce(mockJson.MOCK_USR_DETAIL, HTTP_STATUS(200));
    await services.login(MOCK_CRED)
      .then(ret => {
        expect(ret[0]).toEqual(services.TktEntType.User);
        expect(ret[1].uuid).toEqual(mockJson.MOCK_USR_DETAIL.uuid);
      });
    fetch.mockResponseOnce(mockJson.MOCK_AGT_DETAIL, HTTP_STATUS(200));
    await services.login(MOCK_CRED)
      .then(ret => {
        expect(ret[0]).toEqual(services.TktEntType.Agent);
        expect(ret[1].agent.email).toEqual(mockJson.MOCK_AGT_DETAIL.agent.email);
      });
    fetch.mockResponseOnce(mockJson.MOCK_AMN_DETAIL, HTTP_STATUS(200));
    await services.login(MOCK_CRED)
      .then(ret => {
        expect(ret[0]).toEqual(services.TktEntType.Admin);
        expect(ret[1].admin.email).toEqual(mockJson.MOCK_AMN_DETAIL.admin.email);
      });

      // Should return [null, <Status code w/ error JSON>] on failures
      fetch.mockResponseOnce({message: 'fail'}, HTTP_STATUS(400));
      await services.login({})
        .then(ret => {
          expect(ret[0]).toEqual(null);
          expect(ret[1].status_code).toEqual(400);
          expect(ret[1].message).toEqual('fail');
        });
  });

  test.skip('entity logout', () => {
    return
  });

  test.skip('user details', () => {
    return
  });

  test.skip('event details', () => {
    return
  });

  test.skip('event list', () => {
    return
  });

  test.skip('users registered to an event', () => {
    return
  });

  test.skip('agents registered to an event', () => {
    return
  });

  test.skip('admins registered to an event', () => {
    return
  });

  test.skip('new event creation', () => {
    return
  });
});


describe('utility services', () => {
  test.skip('fetch() wrapper', () => {
    return
  });

  test.skip('initial csrf setter', () => {
    return
  });

  test.skip('get locally saved TOTP secret', () => {
    return
  });

  test.skip('locally save TOTP secret', () => {
    return
  });
});