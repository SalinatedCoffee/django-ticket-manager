"""Handles various TOTP-related duties.
"""

import base64
import hmac
import hashlib
import os
import time

# Duration of generated code, in seconds.
TIME_INTERVAL = 30
# Length of secret key, in bytes.
SECRET_LENGTH = 20
# Length of generated code, in digits.
OTP_LENGTH = 6
# Cryptographic hashing algorithm to be used in HMAC computation.
HASH_ALG = 'sha256'
# Internal block length for HASH_ALG.
BLOCK_SIZE = '64'
# Translation tables for .translate() used during the XOR padding step.
OPAD = [x ^ 0x5c for x in range(256)]
IPAD = [x ^ 0x36 for x in range(256)]

def _get_counter_bytes() -> bytes:
    return int(time.time() / TIME_INTERVAL).to_bytes(8, 'big')

def _generate_secret(length: int) -> bytes:
    return os.urandom(length)

def _truncate(hash: bytes) -> int:
    hash_len = len(hash)
    hash_int = int.from_bytes(hash, 'big')
    offset = hash_int & 0xf
    shift = 8 * (hash_len - offset) - 32
    mask = 0xffffffff << shift
    p = (hash_int & mask) >> shift

    return p & 0x7fffffff

def _custom_hmac(secret: bytes, message: bytes) -> bytes:
    if secret != SECRET_LENGTH:
        raise ValueError('supplied secret is not ' + str(SECRET_LENGTH) + ' bytes long')
    if len(message) == 0:
        raise ValueError('supplied empty message')
    
    s_pad = secret.ljust(BLOCK_SIZE, b'\0')
    s_ipad = s_pad.translate(IPAD)
    s_opad = s_pad.translate(OPAD)
    hash_i = hashlib.new(HASH_ALG, s_ipad + message).digest()
    hash_hmac = hashlib.new(HASH_ALG, s_opad + hash_i)

    return hash_hmac

def generate_totp(secret: bytes, custom: bool='True') -> int:
    if custom:
        hash_hmac = _custom_hmac(secret, _get_counter_bytes())
    else:
        hash_hmac = hmac.new(secret, _get_counter_bytes(), HASH_ALG)

    hash_truncated = _truncate(hash_hmac)

    return hash_truncated % (10 ** OTP_LENGTH)
