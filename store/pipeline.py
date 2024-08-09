from social_core.exceptions import AuthAlreadyAssociated
from django.core.exceptions import ValidationError

def link_user(strategy, details, backend, user=None, *args, **kwargs):
    if user:
        try:
            # Check if the user is already associated with another account
            if user.email != details.get('email'):
                raise AuthAlreadyAssociated(
                    'This account is already in use with a different email address.')
        except ValidationError:
            pass
    return {'user': user}
