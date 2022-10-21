from django.test import TestCase
from django.utils import timezone
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
        self.assertEquals(custom_totp, pyhmac_totp)
        # Check whether TOTP codes of correct length are generated
        self.assertEquals(len(str(custom_totp)), 6)
        # Check if different TOTP codes are generated for different secrets
        self.assertNotEquals(custom_totp, custom_totp2)
    
    def test_ticket_secret_generation(self):
        ev = Event.objects.create(ev_title="Some Event",
                                  ev_description="Some event description",
                                  ev_datetime=timezone.datetime.now(timezone.utc),
                                  ev_hash='1234ABCD5678EFGH')
        ev_shallow = Event(ev_title="Title", ev_description="Description",
                           ev_datetime=timezone.datetime.now(timezone.utc),
                           ev_hash='1234123412341234')
        user = TktUser.objects.create_user('user', 'user@domain.com', 'userpassword')
        user_shallow = TktUser('username', 'email', 'password')
        user_shallow.is_active = False

        with self.assertRaises(ValueError):
            services.generate_ticket_secret(user, ev_shallow)
        with self.assertRaises(ValueError):
            services.generate_ticket_secret(user_shallow, ev)
        with self.assertRaises(ValueError):
            services.generate_ticket_secret(user_shallow, ev_shallow)

        tkt_secret = services.generate_ticket_secret(user, ev)
        
        self.assertEqual(len(tkt_secret), 20)
        self.assertEqual(tkt_secret[:10], b'CD5678EFGH')
        self.assertEqual(tkt_secret[-10:], bytes(user.password[-10:], encoding='utf-8'))
