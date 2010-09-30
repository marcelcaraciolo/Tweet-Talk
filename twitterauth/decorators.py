# -*- charset: utf8 -*-

try:
    from functools import update_wrapper
except ImportError:
    from django.utils.functional import update_wrapper # Python 2.3, 2.4 fallback.
from django.http import HttpResponseRedirect
from django.conf import settings
from django.utils.http import urlquote
from twitterauth import REDIRECT_FIELD_NAME

def login_required(function, redirect_field_name=REDIRECT_FIELD_NAME):
    def f(request, *args, **kwargs):
        if request.user.is_authenticated():
            return function(request, *args, **kwargs)
        path = urlquote(request.get_full_path())
        return HttpResponseRedirect('%s?%s=%s' % (settings.LOGIN_URL, redirect_field_name, path))
    return update_wrapper(f, function)
