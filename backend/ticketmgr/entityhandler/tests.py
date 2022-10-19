from django.test import TestCase
from django.utils import timezone
from entityhandler.models import *

TEST_EV_DATETIME = timezone.datetime.now(timezone.utc)
TEST_EV_HASH = 'ABCD1234ABCD1234'   


class EventsTestCase(TestCase):
    def setUp(self):
        Event.objects.create(ev_title = "Event 1",
                             ev_description = "This is the first event.",
                             ev_datetime = TEST_EV_DATETIME,
                             ev_hash = TEST_EV_HASH)
        Event.objects.create(ev_title = "Event 2",
                             ev_description = "This is the second event.",
                             ev_datetime = timezone.datetime.now(timezone.utc),
                             ev_hash = TEST_EV_HASH)
        Event.objects.create(ev_title = "Event 3",
                             ev_description = "This is the third event.",
                             ev_datetime = timezone.datetime(9876, 5, 4,
                                                             3, 2, 1,
                                                             tzinfo=timezone.utc),
                             ev_hash = TEST_EV_HASH)

    def test_events_attrib_access(self):
        ev1 = Event.objects.get(ev_title = "Event 1")
        ev2 = Event.objects.get(ev_title = "Event 2")
        ev3 = Event.objects.get(ev_title = "Event 3")

        # Test attribute access
        self.assertEqual(ev1.ev_title, "Event 1")
        self.assertEqual(ev1.ev_description, "This is the first event.")
        self.assertEqual(ev1.ev_datetime, TEST_EV_DATETIME)
        self.assertEqual(ev1.ev_hash, TEST_EV_HASH)

        # Test attribute access on different object
        self.assertEqual(ev3.ev_title, "Event 3")
        # Test correct DateTimeField behavior
        self.assertEqual(ev3.ev_datetime, timezone.datetime(9876, 5, 4,
                                                            3, 2, 1,
                                                            tzinfo=timezone.utc))

        # Test invalid lookup query
        with self.assertRaises(Event.DoesNotExist):
            Event.objects.get(ev_title = "Some other event")

class TktEntityTestCase(TestCase):
    def setUp(self):
        ev = Event.objects.create(ev_title = "Some Event",
                                  ev_description = "Dummy event instance for testing",
                                  ev_datetime = TEST_EV_DATETIME,
                                  ev_hash = TEST_EV_HASH)
        TktUser.objects.create_user('username', 'user@somedomain.com', 'userpassword')
        TktAdmin.objects.create_user('adminname', 'admin@somedomain.com', 'adminpassword')
        TktAgent.objects.create_user('agentname', 'agent@somedomain.com', 'agentpassword',
                                event = ev)

    def test_user_entity_model(self):
        user = TktUser.objects.get(username = 'username')
        
        self.assertEqual(user.email, 'user@somedomain.com')

    def test_admin_entity_model(self):
        admin = TktAdmin.objects.get(username = 'adminname')

        self.assertEqual(admin.email, 'admin@somedomain.com')

    def test_agent_entity_model(self):
        agent = TktAgent.objects.get(username = 'agentname')
        event = Event.objects.get(ev_title = "Some Event")

        self.assertEqual(agent.email, 'agent@somedomain.com')
        self.assertEqual(agent.event, event)
