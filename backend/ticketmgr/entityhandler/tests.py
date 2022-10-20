from django.test import TestCase
from django.utils import timezone
from entityhandler.models import *

TEST_EV_DATETIME = timezone.datetime.now(timezone.utc)
TEST_EV_HASH = 'ABCD1234ABCD1234'   


class EventsTestCase(TestCase):
    def setUp(self):
        Event.objects.create(ev_title="Event 1",
                             ev_description="This is the first event.",
                             ev_datetime=TEST_EV_DATETIME,
                             ev_hash=TEST_EV_HASH)
        Event.objects.create(ev_title="Event 2",
                             ev_description="This is the second event.",
                             ev_datetime=timezone.datetime.now(timezone.utc),
                             ev_hash=TEST_EV_HASH)
        Event.objects.create(ev_title="Event 3",
                             ev_description="This is the third event.",
                             ev_datetime=timezone.datetime(9876, 5, 4,
                                                           3, 2, 1,
                                                           tzinfo=timezone.utc),
                             ev_hash=TEST_EV_HASH)

    def test_events_attrib_access(self):
        ev1 = Event.objects.get(ev_title="Event 1")
        ev2 = Event.objects.get(ev_title="Event 2")
        ev3 = Event.objects.get(ev_title="Event 3")

        # Test attribute access
        self.assertEqual(ev1.ev_title, "Event 1")
        self.assertEqual(ev1.ev_description, "This is the first event.")
        self.assertEqual(ev1.ev_datetime, TEST_EV_DATETIME)
        self.assertEqual(ev1.ev_hash, TEST_EV_HASH)

        # Test attribute access on different object
        self.assertEqual(ev3.ev_title, "Event 3")
        # Test correct DateTimeField behavior
        self.assertEqual(ev3.ev_datetime, 
                         timezone.datetime(9876, 5, 4,
                                           3, 2, 1,
                                           tzinfo=timezone.utc))

        # Test invalid lookup query
        with self.assertRaises(Event.DoesNotExist):
            Event.objects.get(ev_title="Some other event")


class TktEntityTestCase(TestCase):
    def setUp(self):
        ev = Event.objects.create(ev_title="Some Event",
                                  ev_description="Dummy event instance for testing",
                                  ev_datetime=TEST_EV_DATETIME,
                                  ev_hash=TEST_EV_HASH)
        TktUser.objects.create_user('username',
                                    'user@somedomain.com',
                                    'userpassword')
        TktAdmin.objects.create_user('adminname',
                                     'admin@somedomain.com',
                                     'adminpassword')
        TktAgent.objects.create(agent=User.objects.create_user(
                                      'agentname',
                                      'agent@somedomain.com',
                                      'agentpassword'),
                                event=ev)

    def test_user_entity_model(self):
        user = TktUser.objects.get(username='username')
        
        self.assertEqual(user.email, 'user@somedomain.com')

    def test_admin_entity_model(self):
        admin = TktAdmin.objects.get(username='adminname')

        self.assertEqual(admin.email, 'admin@somedomain.com')

    def test_agent_entity_model(self):
        agent = User.objects.get(username='agentname')
        event = Event.objects.get(ev_title="Some Event")

        self.assertEqual(agent.email, 'agent@somedomain.com')
        self.assertEqual(agent.tktagent.event, event)


class ModelRelationshipTestCase(TestCase):
    def setUp(self):
        evs = []
        users = []
        admins = []
        for i in range(1, 4):
            evs.append(Event.objects.create(ev_title=f"Event {i}",
                                            ev_description=f"This is event number {i}.",
                                            ev_datetime=TEST_EV_DATETIME,
                                            ev_hash=TEST_EV_HASH))
            users.append(TktUser.objects.create_user(f'user{i}',
                                                     f'user{i}@domain.com',
                                                     f'user{i}password'))
            admins.append(TktAdmin.objects.create_user(f'admin{i}',
                                                       f'admin{i}@domain.com',
                                                       f'admin{i}password'))
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
            Event.objects.create(ev_title=f"Event {i}",
                                 ev_description=f"This is event number {i}.",
                                 ev_datetime=TEST_EV_DATETIME,
                                 ev_hash=TEST_EV_HASH)
            users.append(
                TktUser.objects.create_user(f'user{i}',
                                            f'user{i}@domain.com',
                                            f'password{i}'))
        evs.append(Event.objects.get(ev_title="Event 1"))
        evs.append(Event.objects.get(ev_title="Event 2"))
        for i in range(1, 3):
            user = User.objects.create_user(f'agent{i}',
                                            f'agent{i}@domain.com',
                                            f'password{i}')
            agents.append(TktAgent.objects.create(agent=user, event=evs[i-1]))
        users[0].events.add(evs[0], evs[1])
        users[1].events.add(evs[0])

    def test_event_methods(self):
        ev1 = Event.objects.get(ev_title="Event 1")
        ev2 = Event.objects.get(ev_title="Event 2")
        user1 = TktUser.objects.get(username='user1')
        user2 = TktUser.objects.get(username='user2')
        agent1 = User.objects.get(username='agent1').tktagent
        agent2 = User.objects.get(username='agent2').tktagent

        self.assertTrue(ev1.agent_is_registered(agent1))
        self.assertFalse(ev1.agent_is_registered(agent2))
        self.assertTrue(ev1.user_is_registered(user1))
        self.assertFalse(ev2.user_is_registered(user2))
        self.assertTrue(user1.registered_to_event(ev1))
        self.assertFalse(user2.registered_to_event(ev2))

    def test_tktuser_methods(self):
        ev1 = Event.objects.get(ev_title="Event 1")
        ev2 = Event.objects.get(ev_title="Event 2")
        user1 = TktUser.objects.get(username='user1')
        user2 = TktUser.objects.get(username='user2')

        self.assertTrue(user1.registered_to_event(ev1))
        self.assertFalse(user2.registered_to_event(ev2))
