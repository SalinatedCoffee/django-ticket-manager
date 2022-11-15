#TODO: Refactor tests using self.<var> in setup method
import uuid
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from .models import *
from .views import *

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

class CheckRegistrationTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        evs = []
        users = []
        agents = []
        for i in range(1, 3):
            Event.objects.create(title=f"Event {i}",
                                 description=f"This is event number {i}.",
                                 datetime=TEST_EV_DATETIME)
            users.append(
                TktUser.objects.create(user=User.objects.create_user(f'user{i}',
                                            f'user{i}@domain.com',
                                            f'password{i}')))
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

class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
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
        response = self.client.get('/api/user/user1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user']['first_name'], 'John1')
        # Test valid TktUser request for non-existing user
        response = self.client.get('/api/user/no_user')
        self.assertEqual(response.status_code, 404)
        # Test correct handling of non-TktUser request attempts
        response = self.client.get('/api/user/admin1')
        self.assertEqual(response.status_code, 404)
        # Test correct handling of requests with unsupported methods
        response = self.client.post('/api/user/user1', {'name': 'payload'})
        self.assertEqual(response.status_code, 405)

        # /api/user/<str>/event
        for i in range(3): self.users[0].events.add(self.events[i])
        self.users[1].events.add(self.events[0])
        # Test valid Event request for existing TktUser
        response = self.client.get(f'/api/user/{self.users[0].user.username}/event')
        self.assertEqual(len(response.data), 3)
        # Test valid Event request for non-existing user
        response = self.client.get('/api/user/no_user/event')
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
        response = self.client.post('/api/user', tu_data)
        self.assertEqual(response.status_code, 201)
        post_uuid = response.data['uuid']
        expected_tktuser = TktUser.objects.get(uuid=post_uuid)
        self.assertEqual(expected_tktuser.user.email, tu_data['email'])
        # Test malformed POST request
        response = self.client.post('/api/user', {'blob': 'malformed payload'})
        self.assertEqual(response.status_code, 409)
        # Test POST request with colliding username
        response = self.client.post('/api/user', tu_data)
        self.assertEqual(response.status_code, 409)

        # /api/user/<str>/event
        # Test request to invalid username
        ev_data = {'event_uuid': str(uuid.uuid4)}
        response = self.client.post('/api/user/no_user/event', ev_data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error'], 'User does not exist.')
        # Test valid POST request
        count_expected = self.users[0].events.count() + 1
        ev_uuid = self.events[0].uuid
        ev_data = {'event_uuid': str(ev_uuid)}
        response = self.client.post(f'/api/user/{self.users[0].user.username}/event',
                                    ev_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['uuid'], str(ev_uuid))
        self.assertEqual(self.users[0].events.count(), count_expected)
        # Test valid POST request with non-existant event
        ev_data = {'event_uuid': str(uuid.uuid4)}
        response = self.client.post(f'/api/user/{self.users[0].user.username}/event',
                                    ev_data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error'], 'Event does not exist.')
        # Test POST request with malformed payload
        ev_data = {'uuid_event': str(self.events[0].uuid)}
        response = self.client.post(f'/api/user/{self.users[0].user.username}/event',
                                    ev_data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error'], 'Event does not exist.')


    def test_event_get_endpoints(self):
        self.assertTrue(True)

    def test_event_post_endpoints(self):
        self.assertTrue(True)
