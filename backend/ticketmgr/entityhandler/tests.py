from django.test import TestCase
from django.utils import timezone
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
