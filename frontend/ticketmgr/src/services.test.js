import * as mockJson from './mockJson';
import * as services from './services';

const HTTP_STATUS = (code) => { return {status: code} }

describe('backend interaction services', () => {
  test.skip('new user registration', async () => {
    // Should return [true, <TktUser JSON>] on success
    fetch.mockResponseOnce(mockJson.MOCK_USR_DETAIL, HTTP_STATUS(201));
    await services.register(mockJson.MOCK_USR_REG)
      .then(ret => {
        expect(ret[0]).toBe(true);
        expect(ret[1].uuid).toBe(mockJson.MOCK_USR_DETAIL.uuid);
        expect(ret[1].user.username)
          .toBe(mockJson.MOCK_USR_DETAIL.user.username);
      });
    
    // Should return [false, <Error JSON>] on failure w/ malformed payload
    fetch.mockResponseOnce({message: 'fail'}, HTTP_STATUS(400));
    await services.register(mockJson.MOCK_USR_REG)
      .then(ret => {
        expect(ret[0]).toBe(false);
        expect(ret[1].message).toBe('fail');
      });

    // Should return [false, null] on miscellaneous failures
    fetch.mockResponseOnce({}, HTTP_STATUS(500));
    await services.register(mockJson.MOCK_USR_REG)
      .then(ret => {
        expect(ret[0]).toBe(false);
        expect(ret[1]).toBe(null);
      });
  });

  test.skip('entity login', () => {
    return
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