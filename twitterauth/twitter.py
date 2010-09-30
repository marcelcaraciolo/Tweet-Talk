# -*- charset: utf8 -*-

import oauth
import httplib
import urllib
import exceptions
from django.conf import settings

from django.utils import simplejson as json

if not hasattr(settings, 'TWITTERAUTH_KEY') and \
       hasattr(settings, 'TWITTERAUTH_SECRET'):
    raise ImproperlyConfigured('Django twitterauth requires TWITTERAUTH_KEY and TWITTERAUTH_SECRET to be set in settings.py')

TWITTER_REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
TWITTER_AUTHORIZE_URL = 'https://api.twitter.com/oauth/authorize'
TWITTER_ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
TWITTER_VERIFY_CREDENTIALS_URL = 'https://api.twitter.com/account/verify_credentials.json'

# Timeline Methods
TWITTER_PUBLIC_TIMELINE = "https://api.twitter.com/statuses/public_timeline.json"
TWITTER_FRIENDS_TIMELINE = "https://api.twitter.com/statuses/friends_timeline.json"
TWITTER_FRIENDS_IDS = "http://api.twitter.com/1/friends/ids.json"
TWITTER_FRINEDS_LOOKUP = "http://api.twitter.com/1/users/lookup.json"
TWITTER_USER_TIMELINE = "http://api.twitter.com/1/statuses/user_timeline.json"
# Status Methods
TWITTER_UPDATE_STATUS = 'https://api.twitter.com/statuses/update.json'
TWITTER_RETWEET_STATUS = 'http://api.twitter.com/1/statuses/retweet/%s.json'
TWITTER_UNFOLLOW = "http://api.twitter.com/1/friendships/destroy.json"
# User Methods
TWITTER_FRIENDS = 'https://api.twitter.com/statuses/friends.json'
TWITTER_FOLLOWERS = 'https://api.twitter.com/statuses/followers.json'

TWITTER_SHOW_USER = 'http://api.twitter.com/1/users/show.json'

class TwitterException(exceptions.Exception):
    """If a call to Twitter's RESTful API returns anything other than "200 OK,"
    raise this exception to pass the HTTP status and payload to the caller."""
    def __init__(self, status, reason, payload):
        self.args = (status, reason, payload)
        self.status = status
        self.reason = reason
        self.payload = payload


class TwitterAPI(object):
    def __init__(self, token=None):
        self.consumer = oauth.OAuthConsumer(settings.TWITTERAUTH_KEY, settings.TWITTERAUTH_SECRET)
        self.conn = None
        self.signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()
        self.token = token

    @property
    def connection(self):
        if not self.conn:
            self.conn = httplib.HTTPSConnection('twitter.com')
        return self.conn
    
    @property
    def normal_connection(self):
        if not self.conn:
            self.conn = httplib.HTTPConnection('twitter.com')
        return self.conn

    def get_request(self, url, parameters=None, method='GET', token=None):
        if token is None:
            token = self.token
        if parameters is None:
            parameters = {}
            
        request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=token, 
                     http_url=url, parameters=parameters, http_method=method)
        request.sign_request(self.signature_method, self.consumer, token)
        return request

    def make_request(self, url, parameters=None, method='GET', token=None, connection=None):
        if token is None:
            token = self.token
        if parameters is None:
            parameters = {}
            
        request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=token, 
                     http_url=url, parameters=parameters, http_method=method)
        request.sign_request(self.signature_method, self.consumer, token)
        return self._make_request(connection or self.connection, request.http_method, request.to_url())

    def _make_request(self, connection, http_method, request):
        connection.request(http_method, request)
        response = self.connection.getresponse()
        result = response.read()
        if response.status != 200:
            raise TwitterException(response.status, response.reason, result)
        return result

    def get_request_token(self, callback=None):
        request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, 
                                                             http_url=TWITTER_REQUEST_TOKEN_URL,
                                                             callback=callback)
        request.sign_request(self.signature_method, self.consumer, None)
        return oauth.OAuthToken.from_string(self._make_request(self.connection, request.http_method, request.to_url()))

    def get_authorization_url(self, request_token):
        request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=request_token,
                                                             http_url=TWITTER_AUTHORIZE_URL)
        request.sign_request(self.signature_method, self.consumer, request_token)
        return request.to_url()

    def get_access_token(self, request_token, verifier=None):
        request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=request_token,
                                                             http_url=TWITTER_ACCESS_TOKEN_URL,
                                                             verifier=verifier)
        request.sign_request(self.signature_method, self.consumer, request_token)
        return oauth.OAuthToken.from_string(self._make_request(self.connection, request.http_method, request.to_url()))

    def verify_credentials(self):
        return json.loads(self.make_request(TWITTER_VERIFY_CREDENTIALS_URL))
    
    def tweet(self, status):
        return self.make_request(
            TWITTER_UPDATE_STATUS,
            method='POST',
            parameters=dict(status=status)
        )
    
    def retweet(self, id):
        return self.make_request(
            TWITTER_RETWEET_STATUS % id,
            method='POST',
        )
        
    def friends(self, screen_name):
        return self.make_request(
            TWITTER_FRIENDS,
            parameters=dict(screen_name=screen_name)
        )
        
    def friends_ids(self, screen_name):
        return self.make_request(
            TWITTER_FRIENDS_IDS,
            parameters=dict(screen_name=screen_name)
        )
    
    def friends_lookup(self, friends):
        return self.make_request(
            TWITTER_FRINEDS_LOOKUP,
            parameters=dict(user_id=",".join(friends))
        )
        
    def unfollow(self, id):
        return self.make_request(
            TWITTER_UNFOLLOW,
            method='POST',
            parameters=dict(user_id=id)
        )
        
    def get_user(self, id_or_screen_name):
        return self.make_request(
            TWITTER_SHOW_USER,
            parameters=dict(id=id_or_screen_name)
        )
        
    def get_user_timeline(self, id_or_screen_name, count=10, since_id=""):
        return self.make_request(
            TWITTER_USER_TIMELINE,
            parameters=dict(id=id_or_screen_name, 
                            count=count, 
                            since_id=since_id or ""),
            connection=self.normal_connection
        )
            
        
    
