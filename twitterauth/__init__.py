import datetime
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth import load_backend, get_backends, authenticate


SESSION_KEY = '_twitterauth_user_id'
BACKEND_SESSION_KEY = '_twitterauth_user_backend'
REDIRECT_FIELD_NAME = 'next'


def login(request, user):
    """
    Persist a user id and backend in the request. This way a user doesn't
    have to reauthenticate on every request.
    """
    if user is None:
        user = request.user
        
    #print 'session ', dict(request.session)
    #print 'user.id ', user.id
    if SESSION_KEY in request.session:
        if request.session[SESSION_KEY] != user.id:
            # To avoid reusing another user's session, create a new, empty
            # session if the existing session corresponds to a different
            # authenticated user.
            request.session.flush()
            #print 'Flushssssession...'
    else:
        request.session.cycle_key()
    request.session[SESSION_KEY] = user.id
    request.session[BACKEND_SESSION_KEY] = user.backend
    #print 'session: ', dict(request.session)
    #print 'hasattr: ', hasattr(request, 'user')
    if hasattr(request, 'user'):
        request.user = user


def logout(request):
    """
    Removes the authenticated user's ID from the request an flushes their
    session data.
    """
    request.session.flush()
    if hasattr(request, 'user'):
        from twitterauth.models import AnonymousUser
        request.user = AnonymousUser()


def get_user(request):
    from twitterauth.models import AnonymousUser
    try:
        user_id = request.session[SESSION_KEY]
        backend_path = request.session[BACKEND_SESSION_KEY]
        backend = load_backend(backend_path)
        user = backend.get_user(user_id) or AnonymousUser()
    except KeyError:
        user = AnonymousUser()
    return user
