# -*- charset: utf8 -*-

def auth(request):
    return {'user': request.user }