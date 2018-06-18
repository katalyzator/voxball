from django.core.validators import validate_email


def valid_email(email):
    try:
        validate_email(email)
        return True
    except:
        return False
