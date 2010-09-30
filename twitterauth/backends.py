# -*- charset: utf8 -*-

from models import User

class TwitterBackend(object):
    """
    Authenticates against twitter.
    """
    def authenticate(self, key=None, secret=None):
        try:
            user = User.objects.get(key=key, secret=secret)
            if user.is_twauthorized():
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
