from django.contrib.auth.models import User
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
        ev = Event.objects.create(title="Some Event",
                                  description="Some event description",
                                  datetime=timezone.datetime.now(timezone.utc))
        ev_shallow = Event(title="Title",
                           description="Description",
                           datetime=timezone.datetime.now(timezone.utc))
        django_user = User.objects.create_user('user999', 'user999@domain.com',
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
        self.assertEqual(tkt_secret[:10], bytes(str(ev.uuid)[-10:], encoding='utf-8'))
        self.assertEqual(tkt_secret[-10:], bytes(str(user.uuid)[-10:], encoding='utf-8'))
