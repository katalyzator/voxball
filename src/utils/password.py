import hashlib
import random
import string


def hash_password(password):
    return hashlib.md5(password).hexdigest()


def generate_password(length=8):
    chars = string.ascii_letters + string.digits
    rnd = random.SystemRandom()
    return ''.join(rnd.choice(chars) for _ in range(length))


def generate_sms_code(length=6):
    chars = string.digits
    rnd = random.SystemRandom()
    return ''.join(rnd.choice(chars) for _ in range(length))


def generate_poll_private_code(length=10):
    chars = string.ascii_letters + string.digits
    rnd = random.SystemRandom()
    return ''.join(rnd.choice(chars) for _ in range(length))
