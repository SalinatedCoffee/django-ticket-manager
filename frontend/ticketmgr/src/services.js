// Backend interaction

const ENDPOINT_URI = "http://localhost:8000/api/"

export const TktEntType = {
    // enum for usertypes
    User: Symbol("tktuser"),
    Agent: Symbol("tktagent"),
    Admin: Symbol("tktadmin")
};

export async function register(info) {
    // this should create a new tktuser account given json as input
    // return true and valid json obj on success
    // other entity types are currently unsupported by endpoint
    fetch(ENDPOINT_URI+"user", JSON.stringify(info))
      .then(response => {
        if (response.status !== 200) return (false, response.body.json())
        else return (true, response.body.json())
      })
}

export async function login() {
    // this should log a user in given json as input
    // return true on success
    return
}

export async function logout() {
    // this should log a user out
    // return true on success
    return
}

export async function entityDetails() {
    // this should fetch user details given username
    // return valid json on success with tkt-entity type embedded
    return
}

export async function eventDetails() {
    // this should fetch event details given uuid
    // return valid json on success (including uuid)
    return
}

export async function eventList() {
    // this should fetch list of all events
    // return valid json on success
    // {ev details}, {ev details}, ...
    return
}

export async function eventRegisteredEntityList() {
    // this should fetch list of all entities enrolled to event given uuid
    // return valid json on success
    return
}

export async function createNewEvent() {
    // this should create new event given json
    // return true, valid json on success
    return
}

// Local operations

export function saveTotpSecret() {
    // this should save totp to safe local storage given event uuid
    // return true on success
    return
}

export function getTotpSecret() {
    // this should retrieve totp from local storage
    // return totp on success, false otherwise
    return
}