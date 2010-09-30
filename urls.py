from django.conf.urls.defaults import *

urlpatterns = patterns('',
    ('^$', 'django.views.generic.simple.direct_to_template',
     {'template': 'home.html'}),
    url(r'^tweettalk/callback?$', 'core.views.tweet_talk_callback', name='api_callback'),
)
