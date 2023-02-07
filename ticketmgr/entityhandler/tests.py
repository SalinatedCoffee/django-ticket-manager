#TODO: Refactor tests using self.<var> in setup method
import uuid

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from .models import *

TEST_EV_DATETIME = timezone.datetime.now(timezone.utc)

class EventsTestCase(TestCase):
    def setUp(self):
        Event.objects.create(title="Event 1",
                             description="This is the first event.",
                             datetime=TEST_EV_DATETIME)
        Event.objects.create(title="Event 2",
                             description="This is the second event.",
                             datetime=timezone.datetime.now(timezone.utc))
        Event.objects.create(title="Event 3",
                             description="This is the third event.",
                             datetime=timezone.datetime(9876, 5, 4,
                                                        3, 2, 1,
                                                        tzinfo=timezone.utc))

    def test_events_attrib_access(self):
        ev1 = Event.objects.get(title="Event 1")
        ev2 = Event.objects.get(title="Event 2")
        ev3 = Event.objects.get(title="Event 3")

        # Test attribute access
        self.assertEqual(ev1.title, "Event 1")
        self.assertEqual(ev1.description, "This is the first event.")
        self.assertEqual(ev1.datetime, TEST_EV_DATETIME)
        self.assertIsNotNone(ev1.uuid)

        # Test attribute access on different object
        self.assertEqual(ev3.title, "Event 3")
        # Test correct DateTimeField behavior
        self.assertEqual(ev3.datetime, 
                         timezone.datetime(9876, 5, 4,
                                           3, 2, 1,
                                           tzinfo=timezone.utc))

        # Test invalid lookup query
        with self.assertRaises(Event.DoesNotExist):
            Event.objects.get(title="Some other event")


class TktEntityTestCase(TestCase):
    def setUp(self):
        ev = Event.objects.create(title="Some Event",
                                  description="Dummy event instance for testing",
                                  datetime=TEST_EV_DATETIME)
        TktUser.objects.create(user=User.objects.create_user('username',
                                    'user@somedomain.com',
                                    'userpassword'))
        TktAdmin.objects.create(admin=User.objects.create_user('adminname',
                                     'admin@somedomain.com',
                                     'adminpassword'))
        TktAgent.objects.create(agent=User.objects.create_user(
                                      'agentname',
                                      'agent@somedomain.com',
                                      'agentpassword'),
                                event=ev)

    def test_user_entity_model(self):
        user = User.objects.get(username='username').tktuser
        
        self.assertEqual(user.user.email, 'user@somedomain.com')

    def test_admin_entity_model(self):
        admin = User.objects.get(username='adminname').tktadmin

        self.assertEqual(admin.admin.email, 'admin@somedomain.com')

    def test_agent_entity_model(self):
        agent = User.objects.get(username='agentname').tktagent
        event = Event.objects.get(title="Some Event")

        self.assertEqual(agent.agent.email, 'agent@somedomain.com')
        self.assertEqual(agent.event, event)


class ModelRelationshipTestCase(TestCase):
    def setUp(self):
        evs = []
        users = []
        admins = []
        for i in range(1, 4):
            evs.append(Event.objects.create(title=f"Event {i}",
                                            description=f"This is event number {i}.",
                                            datetime=TEST_EV_DATETIME))
            users.append(TktUser.objects.create(user=User.objects.create_user(f'user{i}',
                                                     f'user{i}@domain.com',
                                                     f'user{i}password')))
            admins.append(TktAdmin.objects.create(admin=User.objects.create_user(f'admin{i}',
                                                       f'admin{i}@domain.com',
                                                       f'admin{i}password')))
        for i in range(1, 4):
            user = User.objects.create_user(f'agent{i}',
                                            f'agent{i}@domain.com',
                                            f'agent{i}password')
            TktAgent.objects.create(agent=user, event=evs[2])


    def test_user_event_m2m(self):
        users = [user for user in TktUser.objects.all()]
        evs = [event for event in Event.objects.all()]

        # All users registered to event 1
        for user in users:
            user.events.add(evs[0])
        # User 1 registered to events 1 and 2
        users[0].events.add(evs[1])

        # Check that users are registered correctly through both models
        self.assertEqual(evs[0].tktuser_set.count(), 3)
        self.assertEqual(users[0].events.count(), 2)

        # Test correct delete behavior
        evs[0].delete()
        self.assertEqual(users[0].events.count(), 1)
        self.assertEqual(users[1].events.count(), 0)
        self.assertEqual(evs[1].tktuser_set.count(), 1)
        users[0].delete()
        self.assertEqual(evs[1].tktuser_set.count(), 0)

    def test_admin_event_m2m(self):
        admins = [admin for admin in TktAdmin.objects.all()]
        evs = [event for event in Event.objects.all()]

        # All admins registered to event 1
        for admin in admins:
            admin.events.add(evs[0])
        # Admin 1 registered to events 1 and 2
        admins[0].events.add(evs[1])

        # Check that admins are registered correctly through both models
        self.assertEqual(evs[0].tktadmin_set.count(), 3)
        self.assertEqual(admins[0].events.count(), 2)

        # Test correct delete behavior
        evs[0].delete()
        self.assertEqual(admins[0].events.count(), 1)
        self.assertEqual(admins[1].events.count(), 0)
        self.assertEqual(evs[1].tktadmin_set.count(), 1)
        admins[0].delete()
        self.assertEqual(evs[1].tktadmin_set.count(), 0)

    def test_agent_event_m2o(self):
        # also remember to check for cascading deletes
        agents = [agent for agent in TktAgent.objects.all()]
        evs = [event for event in Event.objects.all()]

        # Event 1 assigned agents 1 and 2, event 2 assigned agent 3
        evs[0].tktagent_set.add(agents[0], agents[1])
        agents[2].event = evs[1]
        agents[2].save()

        self.assertEqual(evs[0].tktagent_set.count(), 2)
        self.assertEqual(evs[1].tktagent_set.count(), 1)

        # Check correct delete behavior
        evs[0].delete()
        self.assertEqual(TktAgent.objects.count(), 1)
        agents[2].delete()
        self.assertEqual(evs[1].tktagent_set.count(), 0)

class RegistrationCheckTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        evs = []
        users = []
        agents = []
        admins = []
        for i in range(1, 3):
            Event.objects.create(title=f"Event {i}",
                                 description=f"This is event number {i}.",
                                 datetime=TEST_EV_DATETIME)
            users.append(
                TktUser.objects.create(user=User.objects.create_user(f'user{i}',
                                            f'user{i}@domain.com',
                                            f'password{i}')))
            admins.append(
                TktAdmin.objects.create(admin=User.objects.create_user(f'admin{i}',
                                              f'admin{i}@domain.com',
                                              f'password{i}'))
            )
        evs.append(Event.objects.get(title="Event 1"))
        evs.append(Event.objects.get(title="Event 2"))
        for i in range(1, 3):
            user = User.objects.create_user(f'agent{i}',
                                            f'agent{i}@domain.com',
                                            f'password{i}')
            agents.append(TktAgent.objects.create(agent=user, event=evs[i-1]))
        users[0].events.add(evs[0], evs[1])
        users[1].events.add(evs[0])

    def test_event_methods(self):
        ev1 = Event.objects.get(title="Event 1")
        ev2 = Event.objects.get(title="Event 2")
        user1 = User.objects.get(username='user1').tktuser
        user2 = User.objects.get(username='user2').tktuser
        agent1 = User.objects.get(username='agent1').tktagent
        agent2 = User.objects.get(username='agent2').tktagent

        self.assertTrue(ev1.agent_is_registered(agent1))
        self.assertFalse(ev1.agent_is_registered(agent2))
        self.assertTrue(ev1.user_is_registered(user1))
        self.assertFalse(ev2.user_is_registered(user2))
        self.assertTrue(user1.registered_to_event(ev1))
        self.assertFalse(user2.registered_to_event(ev2))

    def test_tktuser_methods(self):
        ev1 = Event.objects.get(title="Event 1")
        ev2 = Event.objects.get(title="Event 2")
        user1 = User.objects.get(username='user1').tktuser
        user2 = User.objects.get(username='user2').tktuser

        self.assertTrue(user1.registered_to_event(ev1))
        self.assertFalse(user2.registered_to_event(ev2))

class EndpointAuthenticationTestCase(TestCase):
    def setUp(self):
        self.ev = Event.objects.create(title='Ev',
                                       description='Ev.',
                                       datetime=timezone.datetime.now(timezone.utc))
        self.client = APIClient()
        self.su = User.objects.create_superuser('test_su', password='password')
        self.u = User.objects.create_user('test_u', password='password')
        self.usr = TktUser.objects.create(user=User.objects.create_user('user1',
                                                                   'user1@domain.com',
                                                                   'user1pass',
                                                                   first_name='John',
                                                                   last_name='Doe'))
        self.agt = TktAgent.objects.create(agent=User.objects.create_user('agent1',
                                                                     'agent1@domain.com',
                                                                     'agent1pass',
                                                                     first_name='Jane',
                                                                     last_name='Doe'),
                                                                     event=self.ev)
        self.amn = TktAdmin.objects.create(admin=User.objects.create_user('admin1',
                                                                     'admin1@domain.com',
                                                                     'admin1pass',
                                                                     first_name='Ad',
                                                                     last_name='Ministrator'))

    def test_authentication_login(self):
        # /api/login
        # Test login as misconfigured Django User
        response = self.client.post('/api/login',
                                    {'username': 'test_u',
                                     'password': 'password'})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.data.get('error'), 'Failed to resolve user type.')
        self.assertIsNone(response.client.cookies.get('sessionid'))
        # Test login as Django Superuser
        response = self.client.post('/api/login',
                                    {'username': 'test_su',
                                     'password': 'password'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('message'), 'Logged in as superuser.')
        self.assertIsNotNone(response.client.cookies.get('sessionid'))
        # Test login as TktUser
        response = self.client.post('/api/login',
                                    {'username': 'user1',
                                     'password': 'user1pass'})
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data.get('user'))
        self.assertIsNotNone(response.client.cookies.get('sessionid'))
        # Test login as TktAgent
        response = self.client.post('/api/login',
                                    {'username': 'agent1',
                                     'password': 'agent1pass'})
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data.get('agent'))
        self.assertIsNotNone(response.client.cookies.get('sessionid'))
        # Test login as TktAdmin
        response = self.client.post('/api/login',
                                    {'username': 'admin1',
                                     'password': 'admin1pass'})
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data.get('admin'))
        self.assertIsNotNone(response.client.cookies.get('sessionid'))
        

    def test_authentication_logout(self):
        response = self.client.post('/api/login',
                                    {'username': 'test_su',
                                     'password': 'password'})
        self.client.cookies = response.client.cookies
        response = self.client.get('/api/event')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/api/logout')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/api/event')
        self.assertEqual(response.status_code, 403)

class EndpointBehaviorTestCase(TestCase):
    def setUp(self):
        SU_UNAME = 'debug_admin'
        SU_PWORD = 'debug_adminpass'
        self.su_client = APIClient()
        User.objects.create_superuser(SU_UNAME, password=SU_PWORD)
        response = self.su_client.post('/api/login',
                                    {'username': SU_UNAME,
                                     'password': SU_PWORD})
        self.su_client.cookies = response.client.cookies
        self.users = []
        self.events = []
        self.admins = []
        self.agents = []
        for i in range(3):
            u = TktUser.objects.create(
                user=User.objects.create_user(f'user{i}',
                                              f'user{i}@domain.com',
                                              f'user{i}pass',
                                              first_name=f'John{i}',
                                              last_name=f'Doe{i}'))
            e = Event.objects.create(title=f'Event {i}',
                                     description=f'This is event {i}.',
                                     datetime=timezone.datetime.now(timezone.utc))
            a = TktAdmin.objects.create(
                admin=User.objects.create_user(f'admin{i}',
                                               f'admin{i}@domain.com',
                                               f'admin{i}pass',
                                               first_name=f'Jane{i}',
                                               last_name=f'Doe{i}'))
            g = TktAgent.objects.create(
                agent=User.objects.create_user(f'agent{i}',
                                               f'agent{i}@domain.com',
                                               f'agent{i}pass',
                                               first_name=f'John{i}',
                                               last_name=f'Appleseed{i}'),
                event=e)
            self.users.append(u)
            self.events.append(e)
            self.admins.append(a)
            self.agents.append(g)

    def test_user_get_endpoints(self):
        # /api/user/<str>
        # Test valid TktUser request for existing user
        response = self.su_client.get('/api/user/user1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user']['first_name'], 'John1')
        # Test valid TktUser request for non-existing user
        response = self.su_client.get('/api/user/no_user')
        self.assertEqual(response.status_code, 404)
        # Test correct handling of non-TktUser request attempts
        response = self.su_client.get('/api/user/admin1')
        self.assertEqual(response.status_code, 404)
        # Test correct handling of requests with unsupported methods
        response = self.su_client.post('/api/user/user1', {'name': 'payload'})
        self.assertEqual(response.status_code, 405)

        # /api/user/<str>/event
        for i in range(3): self.users[0].events.add(self.events[i])
        self.users[1].events.add(self.events[0])
        # Test valid Event request for existing TktUser
        response = self.su_client.get(f'/api/user/{self.users[0].user.username}/event')
        self.assertEqual(len(response.data), 3)
        # Test valid Event request for non-existing user
        response = self.su_client.get('/api/user/no_user/event')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error'], 'User does not exist.')

    def test_user_post_endpoints(self):
        # /api/user
        # Test valid POST request
        tu_data = {'username': 'user_test',
                   'email': 'user_test@domain.com',
                   'first_name': 'test',
                   'last_name': 'user',
                   'password': 'user_testpass'}
        response = self.su_client.post('/api/user', tu_data)
        self.assertEqual(response.status_code, 201)
        post_uuid = response.data['uuid']
        expected_tktuser = TktUser.objects.get(uuid=post_uuid)
        self.assertEqual(expected_tktuser.user.email, tu_data['email'])
        # Test malformed POST request
        response = self.su_client.post('/api/user', {'blob': 'malformed payload'})
        self.assertEqual(response.status_code, 400)
        # Test POST request with colliding username
        response = self.su_client.post('/api/user', tu_data)
        self.assertEqual(response.status_code, 400)

        """
        # /api/user/<str>/event
        # Test request to invalid username
        ev_data = {'event_uuid': str(uuid.uuid4)}
        response = self.su_client.post('/api/user/no_user/event', ev_data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error'], 'User does not exist.')
        # Test valid POST request
        count_expected = self.users[0].events.count() + 1
        ev_uuid = self.events[0].uuid
        ev_data = {'event_uuid': str(ev_uuid)}
        response = self.su_client.post(f'/api/user/{self.users[0].user.username}/event',
                                    ev_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['uuid'], str(ev_uuid))
        self.assertEqual(self.users[0].events.count(), count_expected)
        # Test valid POST request with non-existent event
        ev_data = {'event_uuid': str(uuid.uuid4)}
        response = self.su_client.post(f'/api/user/{self.users[0].user.username}/event',
                                    ev_data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error'], 'Event does not exist.')
        # Test POST request with malformed payload
        ev_data = {'uuid_event': str(self.events[0].uuid)}
        response = self.su_client.post(f'/api/user/{self.users[0].user.username}/event',
                                    ev_data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error'], 'Event does not exist.')
        """

    def test_event_get_endpoints(self):
        # /api/event
        # Test valid GET request
        response = self.su_client.get('/api/event')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), len(self.events))
        ev = Event.objects.get(uuid=response.data[0]['uuid'])
        self.assertEqual(ev.title, response.data[0]['title'])

        # /api/event/<uuid>
        # Test valid GET request
        ev_uuid = self.events[0].uuid
        response = self.su_client.get(f'/api/event/{ev_uuid}')
        self.assertEqual(self.events[0].title, response.data['title'])
        # Test GET request on non-existent event
        response = self.su_client.get(f'/api/event/{uuid.uuid4()}')
        self.assertEqual(response.status_code, 404)

        # /api/event/<uuid>/user
        for i in range(3): self.users[i].events.add(self.events[0])
        # Test valid GET request on event with registered users
        ev_uuid = self.events[0].uuid
        response = self.su_client.get(f'/api/event/{ev_uuid}/user')
        self.assertEqual(len(self.events), len(response.data))
        # Test valid GET request on event with no registered users
        ev_uuid = self.events[1].uuid
        response = self.su_client.get(f'/api/event/{ev_uuid}/user')
        self.assertEqual(self.events[1].tktuser_set.count(), len(response.data))
        # Test GET request on non-existent event
        response = self.su_client.get(f'/api/event/{uuid.uuid4()}/user')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error'], 'Event does not exist.')

        # /api/event/<uuid>/agent
        # Test valid GET request
        ev_uuid = self.events[0].uuid
        response = self.su_client.get(f'/api/event/{ev_uuid}/agent')
        self.assertEqual(response.data[0]['agent']['email'], self.agents[0].agent.email)

        # /api/event/<uuid>/admin
        for i in range(2): self.admins[0].events.add(self.events[i])
        self.admins[1].events.add(self.events[2])
        # Test valid GET request
        ev_uuid = self.events[0].uuid
        response = self.su_client.get(f'/api/event/{ev_uuid}/admin')
        self.assertEqual(self.events[0].tktadmin_set.count(), len(response.data))
        self.assertEqual(response.data[0]['admin']['email'], self.admins[0].admin.email)

    def test_event_post_endpoints(self):
        # /api/event
        # Test valid POST request
        ev_data = {'title': 'POST Event',
                   'description': 'This event was added via API requests.',
                   'datetime': str(timezone.datetime.now(timezone.utc))}
        response = self.su_client.post('/api/event', ev_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['title'], 'POST Event')
        expected_event = Event.objects.get(uuid=response.data['uuid'])
        self.assertEqual(response.data['title'], expected_event.title)
        # Test POST request with malformed payload
        ev_data = {'ev_title': 'POST Event',
                   'ev_description': 'This event was added via API requests.',
                   'ev_datetime': str(timezone.datetime.now(timezone.utc))}
        response = self.su_client.post('/api/event', ev_data)
        self.assertEqual(response.status_code, 400)

        # /api/event/<uuid>/user
        ev_uuid = self.events[0].uuid
        user_uuid = self.users[0].uuid
        post_data = {'user_uuid': str(user_uuid)}
        # Test valid POST request
        response = self.su_client.post(f'/api/event/{ev_uuid}/user', post_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user']['email'], self.users[0].user.email)
        self.assertEqual(self.events[0].uuid,
                         self.users[0].events.filter()[0].uuid)
        # Test valid POST request for non-existent user
        response = self.su_client.post(f'/api/event/{ev_uuid}/user',
                                    {'user_uuid': str(uuid.uuid4)})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error'], 'User does not exist.')
        # Test POST request with malformed payload
        response = self.su_client.post(f'/api/event/{ev_uuid}/user',
                                    {'uuid_user': str(user_uuid)})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error'], 'User does not exist.')

        # /api/event/<uuid>/admin
        ev_uuid = self.events[0].uuid
        admin_uname = self.admins[0].admin.username
        post_data = {'admin_username': admin_uname}
        # Test valid POST request
        response = self.su_client.post(f'/api/event/{ev_uuid}/admin', post_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['admin']['username'], admin_uname)
        self.assertEqual(self.events[0].uuid,
                         self.admins[0].events.filter()[0].uuid)
        # Test valid POST request for non-existent admin
        response = self.su_client.post(f'/api/event/{ev_uuid}/admin',
                                    {'admin_username': 'no_admin'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error'], 'Admin does not exist.')
        # Test valid POST request for existing user username
        response = self.su_client.post(f'/api/event/{ev_uuid}/admin',
                                    {'admin_username': 'user0'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error'], 'Admin does not exist.')
        # Test POST request with malformed payload
        response = self.su_client.post(f'/api/event/{ev_uuid}/admin',
                                    {'username_admin': admin_uname})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error'], 'Admin does not exist.')

class EndpointAuthorizationTestCase(TestCase):
    def util_auth_apiclient(self, username: str, password: str) -> APIClient:
        """Utility function that generates an ``APIClient`` with credentials
        required for token authentication.

        Args:
            username (``str``): Username of the user to authenticate as.
            password (``str``): Password of the user to authenticate as.

        Returns:
            ``APIClient``: ``APIClient`` object with access token authenticating
            the user with provided credentials.
        """
        client = APIClient()
        response = client.post('/api/login',
                               {'username': username, 'password': password})
        if response.status_code != 200:
            raise ValueError('failed to authenticate with provided credentials')
        client.cookies = response.client.cookies
        return client

    def setUp(self):
        self.user = TktUser.objects.create(
                        user=User.objects.create_user('user1', password='user1pass'))
        self.admin = TktAdmin.objects.create(
                        admin=User.objects.create_user('admin1', password='admin1pass'))
        self.event = Event.objects.create(
                        title="Event 1",
                        description="This is the first event.",
                        datetime=timezone.datetime.now(timezone.utc))
        self.agent = TktAgent.objects.create(
                        agent=User.objects.create_user('agent1', password='agent1pass'),
                        event=self.event)
        self.usr_client = self.util_auth_apiclient('user1', 'user1pass')
        self.amn_client = self.util_auth_apiclient('admin1', 'admin1pass')
        self.agt_client = self.util_auth_apiclient('agent1', 'agent1pass')
    
    def test_user_get_endpoints(self):
        usr2 = TktUser.objects.create(user=User.objects.create_user('user2',
                                                                    password='user2pass'))
        usr2_client = self.util_auth_apiclient('user2', 'user2pass')
        # Test user info access as other user
        response = usr2_client.get('/api/user/user1')
        self.assertEqual(response.status_code, 403)
        # Test user info access as self, admin, agent
        response = self.usr_client.get('/api/user/user1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user']['username'], 'user1')
        response = self.amn_client.get('/api/user/user1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user']['username'], 'user1')
        response = self.agt_client.get('/api/user/user1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user']['username'], 'user1')

    """
    def test_user_post_endpoints(self):
        payload = {'event_uuid': str(self.event.uuid)}
        # only admins can post event to user
        # Test event registration by user, agent
        response = self.usr_client.post(f'/api/user/{self.user.user.username}/event', payload)
        self.assertEqual(response.status_code, 403)
        response = self.agt_client.post(f'/api/user/{self.user.user.username}/event', payload)
        self.assertEqual(response.status_code, 403)
        # Test event registration by admin
        response = self.amn_client.post(f'/api/user/{self.user.user.username}/event', payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['uuid'], str(self.event.uuid))
    """

    def test_event_get_endpoints(self):
        # Test event list GET request by user, agent, admin
        response = self.usr_client.get('/api/event')
        self.assertEqual(response.status_code, 200)
        response = self.agt_client.get('/api/event')
        self.assertEqual(response.status_code, 200)
        response = self.amn_client.get('/api/event')
        self.assertEqual(response.status_code, 200)
        ev_uri = f'/api/event/{str(self.event.uuid)}'
        # Test event detail GET request by user, agent, admin
        response = self.usr_client.get(ev_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], self.event.title)
        response = self.agt_client.get(ev_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], self.event.title)
        response = self.amn_client.get(ev_uri)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], self.event.title)
        # Test event admin and user GET request by user
        response = self.usr_client.get(f'{ev_uri}/user')
        self.assertEqual(response.status_code, 403)
        response = self.usr_client.get(f'{ev_uri}/admin')
        self.assertEqual(response.status_code, 403)
        # Test event admin and user GET request by agent, admin
        response = self.agt_client.get(f'{ev_uri}/user')
        self.assertEqual(response.status_code, 200)
        response = self.amn_client.get(f'{ev_uri}/user')
        self.assertEqual(response.status_code, 200)
        response = self.agt_client.get(f'{ev_uri}/admin')
        self.assertEqual(response.status_code, 200)
        response = self.amn_client.get(f'{ev_uri}/admin')
        self.assertEqual(response.status_code, 200)
        # Test event agent GET request by user, agent
        response = self.usr_client.get(f'{ev_uri}/agent')
        self.assertEqual(response.status_code, 403)
        response = self.agt_client.get(f'{ev_uri}/agent')
        self.assertEqual(response.status_code, 403)
        # Test event agent GET request by admin
        response = self.amn_client.get(f'{ev_uri}/admin')
        self.assertEqual(response.status_code, 200)

    def test_event_post_endpoints(self):
        ev_data = {'title': 'POST Event',
                   'description': 'This event was created by a POST api request',
                   'datetime': str(timezone.datetime.now(timezone.utc))}
        # Test event creation by user, agent
        response = self.usr_client.post('/api/event', ev_data)
        self.assertEqual(response.status_code, 403)
        response = self.agt_client.post('/api/event', ev_data)
        self.assertEqual(response.status_code, 403)
        # Test event creation by admin
        response = self.amn_client.post('/api/event', ev_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['title'], ev_data['title'])
        payload = {'user_uuid': str(self.user.uuid)}
        ev_uri = f'/api/event/{self.event.uuid}'
        # Test user event registration by user, agent
        response = self.usr_client.post(f'{ev_uri}/user', payload)
        self.assertEqual(response.status_code, 403)
        response = self.agt_client.post(f'{ev_uri}/user', payload)
        self.assertEqual(response.status_code, 403)
        # Test user event registration by admin
        response = self.amn_client.post(f'{ev_uri}/user', payload)
        self.assertEqual(response.status_code, 200)
        payload = {'admin_username': self.admin.admin.username}
        # Test admin event registration by user, agent
        response = self.usr_client.post(f'{ev_uri}/admin', payload)
        self.assertEqual(response.status_code, 403)
        response = self.agt_client.post(f'{ev_uri}/admin', payload)
        self.assertEqual(response.status_code, 403)
        # Test admin event registration by admin
        response = self.amn_client.post(f'{ev_uri}/admin', payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['admin']['username'], self.admin.admin.username)
