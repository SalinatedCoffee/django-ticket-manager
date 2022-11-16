import uuid

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from entityhandler.models import Event, TktUser
from otphandler import services


class ServicesTestCase(TestCase):
    def test_totp_generation(self):
        test_secret = b'DEBUGSECRETKEY2345=='
        test_secret2 = b'SECRETDEBUGKEY2345=='
        custom_totp = services.generate_totp(test_secret, True)
        custom_totp2 = services.generate_totp(test_secret2, True)
        pyhmac_totp = services.generate_totp(test_secret)

        # Check sanity check behavior of custom HMAC algorithm
        with self.assertRaises(ValueError):
            services.generate_totp(b'', True)
        # Check correct HMAC computation of custom implementation
        self.assertEqual(custom_totp, pyhmac_totp)
        # Check whether TOTP codes of correct length are generated
        self.assertEqual(len(custom_totp), 6)
        # Check if different TOTP codes are generated for different secrets
        self.assertNotEqual(custom_totp, custom_totp2)
    
    def test_ticket_secret_generation(self):
        ev = Event.objects.create(title="Some Event",
                                  description="Some event description",
                                  datetime=timezone.datetime.now(timezone.utc))
        ev_shallow = Event(title="Title",
                           description="Description",
                           datetime=timezone.datetime.now(timezone.utc))
        django_user = User.objects.create_user('user999',
                                               'user999@domain.com',
                                               'user999pass',
                                               first_name='Jane',
                                               last_name='Doe')
        duser_shallow = User('user111', 'user111@domain.com', 'user111pass')
        user = TktUser.objects.create(user=django_user)
        user_shallow = TktUser(duser_shallow)
        user_shallow.is_active = False

        with self.assertRaises(ValueError):
            services.generate_ticket_secret(user, ev_shallow)
        with self.assertRaises(ValueError):
            services.generate_ticket_secret(user_shallow, ev)
        with self.assertRaises(ValueError):
            services.generate_ticket_secret(user_shallow, ev_shallow)

        tkt_secret = services.generate_ticket_secret(user, ev)
        
        self.assertEqual(len(tkt_secret), 20)
        self.assertEqual(tkt_secret[:10],
                         bytes(str(ev.uuid)[-10:], encoding='utf-8'))
        self.assertEqual(tkt_secret[-10:],
                         bytes(str(user.uuid)[-10:], encoding='utf-8'))

class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.ev = Event.objects.create(title="Event 1",
                                  description="This is the first event.",
                                  datetime=timezone.datetime.now(timezone.utc))
        user = User.objects.create_user('user1',
                                        'user1@domain.com',
                                        'user1pass',
                                        first_name='John',
                                        last_name='Doe')
        self.usr = TktUser.objects.create(user=user)

    def test_ticket_new(self):
        # /api/ticket/new
        post_data = {'user_uuid': str(self.usr.uuid),
                     'event_uuid': str(self.ev.uuid)}
        # Test valid POST request with non-existent user
        request = self.client.post('/api/ticket/new',
                                   {'user_uuid': str(uuid.uuid4),
                                    'event_uuid': str(self.ev.uuid)})
        self.assertEqual(request.status_code, 404)
        self.assertEqual(request.data['error'], 'User does not exist.')
        # Test valid POST request with non-existent event
        request = self.client.post('/api/ticket/new',
                                   {'user_uuid': str(self.usr.uuid),
                                    'event_uuid': str(uuid.uuid4)})
        self.assertEqual(request.status_code, 404)
        self.assertEqual(request.data['error'], 'Event does not exist.')
        # Test POST request with malformed payload
        request = self.client.post('/api/ticket/new',
                                   {'uuid_user': str(self.usr.uuid),
                                    'event_uuid': str(self.ev.uuid)})
        self.assertEqual(request.status_code, 404)
        self.assertEqual(request.data['error'], 'User does not exist.')
        # Test valid POST request
        request = self.client.post('/api/ticket/new', post_data)
        self.assertEqual(request.status_code, 200)
        self.assertEqual(len(request.data['success']), 20)
        # Test POST request with already registered event-user pair
        request = self.client.post('/api/ticket/new', post_data)
        self.assertEqual(request.status_code, 409)
        self.assertEqual(request.data['error'], 'User already registered to event.')

    def test_ticket_auth(self):
        # /api/ticket/auth
        post_data = {'user_uuid': str(self.usr.uuid),
                     'event_uuid': str(self.ev.uuid),
                     'ticket_totp': '123456'}
        # Test valid POST request with non-existent user
        request = self.client.post('/api/ticket/auth',
                                   {'user_uuid': str(uuid.uuid4),
                                    'event_uuid': str(self.ev.uuid),
                                    'ticket_totp': '123456'})
        self.assertEqual(request.status_code, 404)
        self.assertEqual(request.data['error'], 'User does not exist.')
        # Test valid POST request with non-existent event
        request = self.client.post('/api/ticket/auth',
                                    {'user_uuid': str(self.usr.uuid),
                                     'event_uuid': str(uuid.uuid4),
                                     'ticket_totp': '123456'})
        self.assertEqual(request.status_code, 404)
        self.assertEqual(request.data['error'], 'Event does not exist.')
        # Test valid POST request with unregistered event-user pair
        request = self.client.post('/api/ticket/auth', post_data)
        self.assertEqual(request.status_code, 400)
        self.assertEqual(request.data['error'], 'User is not registered to event.')
        # Test POST request with malformed payload
        self.usr.events.add(self.ev)
        request = self.client.post('/api/ticket/auth',
                                   {'uuid_user': str(self.usr.uuid),
                                    'event_uuid': str(self.ev.uuid),
                                    'ticket_totp': '123456'})
        self.assertEqual(request.status_code, 404)
        self.assertEqual(request.data['error'], 'User does not exist.')
        post_data['ticket_totp'] = ''
        request = self.client.post('/api/ticket/auth', post_data)
        self.assertEqual(request.status_code, 400)
        self.assertEqual(request.data['error'], 'TOTP code was not supplied.')
        request = self.client.post('/api/ticket/auth',
                                    {'user_uuid': str(self.usr.uuid),
                                     'event_uuid': str(self.ev.uuid)})
        self.assertEqual(request.status_code, 400)
        self.assertEqual(request.data['error'], 'TOTP code was not supplied.')
        # Test valid POST request with correct TOTP
        ticket_secret = services.generate_ticket_secret(self.usr, self.ev)
        post_data = {'user_uuid': str(self.usr.uuid),
                     'event_uuid': str(self.ev.uuid),
                     'ticket_totp': services.generate_totp(ticket_secret)}
        request = self.client.post('/api/ticket/auth', post_data)
        self.assertEqual(request.status_code, 200)
        self.assertTrue(request.data['ticket_is_valid'])
        # Test valid POST request with incorrect TOTP
        post_data['ticket_totp'] = post_data['ticket_totp'][:5].zfill(6)
        request = self.client.post('/api/ticket/auth', post_data)
        self.assertEqual(request.status_code, 200)
        self.assertFalse(request.data['ticket_is_valid'])
