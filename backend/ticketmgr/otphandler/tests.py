from django.test import TestCase
from otphandler import services

class ServicesTestCase(TestCase):
    def test_totp_generation(self):
        test_secret = b'DEBUGSECRETKEY2345=='
        test_secret2 = b'SECRETDEBUGKEY2345=='
        custom_totp = services.generate_totp(test_secret, True)
        custom_totp2 = services.generate_totp(test_secret2, True)
        pyhmac_totp = services.generate_totp(test_secret)

        # Check correct HMAC computation of custom implementation
        assert(custom_totp == pyhmac_totp)
        # Check if different TOTP codes are generated for different secrets
        assert(custom_totp != custom_totp2)
