# -*- charset: utf8 -*-

import urllib
import datetime
import oauth
from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from twitterauth.twitter import TwitterAPI
from django.utils import simplejson


class User(models.Model):
    username = models.CharField(max_length=40)
    thumbnail = models.CharField(max_length=200, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    userkey = models.CharField(max_length=255)
    request_token = models.CharField(max_length=255, null=True, blank=True)
    is_valid = models.BooleanField(default=False)
    last_login = models.DateTimeField(_('last login'), default=datetime.datetime.now)
    date_joined = models.DateTimeField(_('date joined'), default=datetime.datetime.now)

    key = models.CharField(max_length=200, null=True)
    secret = models.CharField(max_length=200, null=True)

    def __unicode__(self):
        return self.username

    _twitter_api = None
    @property
    def twitter_api(self):
        if self._twitter_api is None:
            self._twitter_api = TwitterAPI(oauth.OAuthToken.from_string(self.token()))
        return self._twitter_api

    def get_absolute_url(self):
        return reverse('user', kwargs={'id': self.id})

    def token(self, only_key=False):
        # so this can be used in place of an oauth.OAuthToken
        if only_key:
            return urllib.urlencode({'oauth_token': self.key})
        return urllib.urlencode({'oauth_token': self.key, 'oauth_token_secret': self.secret})

    def get_and_delete_messages(self): pass

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def is_authorized(self): 
        return True
    
    def is_active(self):
        return True
    
    def is_staff(self):
        return self.is_staff
    
    def has_module_perms(self, *args, **kwargs):
        return True
        
    def has_perm(self, *args, **kwargs):
        return True
    
    def is_twauthorized(self):
        return bool(self.twitter_api.verify_credentials())

    def tweet(self, status):
        return simplejson.loads(
            self.twitter_api.tweet(status)
        )
        
    def retweet(self, id):
        return simplejson.loads(
            self.twitter_api.retweet(id)
        )
    
    def friends(self):
        return simplejson.loads(
            self.twitter_api.friends(self.username)
        )
        
    def friends_ids(self):
        return simplejson.loads(
            self.twitter_api.friends_ids(self.username)
        )
        
    def friends_lookup(self, friends_ids):
        return simplejson.loads(
            self.twitter_api.friends_lookup(friends_ids)
        )
        
    def unfollow(self, user_id):
        return simplejson.loads(
            self.twitter_api.unfollow(user_id)
        )
        
    def get_user(self, id_or_screen_name):
        return simplejson.loads(
            self.twitter_api.get_user(id_or_screen_name)
        )
        
    def get_user_timeline(self, id_or_screen_name, count=10, since_id=None):
        return simplejson.loads(
            self.twitter_api.get_user_timeline(id_or_screen_name or self.username, 
                                        count=count, since_id=since_id)
        )

class AnonymousUser(object):
    username = ''
    
    key = ''
    secret = ''

    def __unicode__(self):
        return 'AnonymousUser'

    def to_string(self, only_key=False):
        raise NotImplemented

    _twitter_api = None
    @property
    def twitter_api(self):
        if self._twitter_api is None:
            self._twitter_api = TwitterAPI()
        return self._twitter_api

    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return 1 # instances always return the same hash value

    def save(self):
        raise NotImplemented

    def delete(self):
        raise NotImplemented

    def tweet(self, status):
        raise NotImplemented
    
    def get_and_delete_messages(self): pass

    def is_anonymous(self):
        return True

    def is_authenticated(self):
        return False

    def is_twauthorized(self):
        return False
    
    def is_active(self):
        return True
    
    def is_staff(self):
        return False
