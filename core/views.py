#-*- coding:utf-8 -*-

import base64
import httplib
import urllib
import re
from django.utils import simplejson 
from django.http import HttpResponse
from twitterauth import oauth
from twitterauth.models import User


def send_msg(userkey,tp,resp):
	url = 'www.imified.com'
	
	form_fields = { 
		"botkey": "DCA2809D-E272-4EB9-8272CEFF6C23D231",    # Your bot key goes here.
		"apimethod": "send",  # the API method to call.
		"userkey": str(userkey),  # User Key to lookup with getuser.
		"msg": tp.encode('utf-8'),
		'network' : 'Jabber'
	}
	
	
	# Build the Basic Authentication string.  Don't forget the [:-1] at the end!
	base64string = base64.encodestring('%s:%s' % ('caraciol@gmail.com', 'mpcara'))[:-1]
	authString = 'Basic %s' % base64string
	
	
	# Build the request post data.
	form_data = urllib.urlencode(form_fields)

	# Make the call to the service using httplib command.
	con = httplib.HTTPSConnection(url)
	con.request('POST','/api/bot/', form_data,{'AUTHORIZATION': authString})
	response = con.getresponse()	
	if response.status == 200:
		resp.write(tp)
	else:
		resp.write(response.reason + ' ' +  str(response.status))
		

#(1) Tentar verificar se o usuario ja ta cadastrado com token. Se sim passo 2 se nao passo 3.
#(2) Envia para o usuario. voce se encontra cadastrado. envie sua msg: Va para o passo 4.
#(3) Usuario recebe uma msg: user nao cadastrado, recebe uma url. usuario autoriza, recebe um pincode. envia pincode. Va para passo 2.
#(4) Usuario digita a msg, recebe e ele envia a confirmacao tweet enviado.
def tweet_talk_callback(request,template=""):
	step = int(request.POST.get('step',0))
	userkey = request.POST.get('userkey','')
	msg = request.POST.get('msg','')
	value1 = request.POST.get('value1','')
	user = request.POST.get('user','')
	
	response = HttpResponse()
	
	#(1) Tenta verificar se o usuario ja esta cadastrado com o token. Se sim passo 2 se nao passo 3.
	if userkey:
		#Tem usuario ? Se sim, verificar se tem token valido.
		users = User.objects.filter(userkey__exact = userkey)
		if users:
			userP = users[0]
			if step == 1:				
				#Primeira vez que chegou vamos ver o que fazer
				credentials = userP.twitter_api.verify_credentials()
				if credentials:
					send_msg(userkey, 'Hi %s , from now on you can write your tweet and then it will be posted.'.decode('utf-8') % credentials['screen_name']  , response)
					userP.name = credentials['name']
					userP.screename = credentials['screen_name']
					userP.save()
					response.write('<goto=2>')
				else:
					send_msg(userkey,'Problems in authentication. Try again.',response)
					userP.delete()
					response.write('<goto=1>')
		 	elif step == 2:
				#recebe o pincode
				pattern = re.compile("\\d{7}")
				result = re.findall(pattern,msg)
				if result:
					#tem algum PINCODE, pega o PINCODE
					userP.twitter_api.token = request.user.twitter_api.get_access_token(oauth.OAuthToken.from_string(userP.request_token), verifier=result[0])
					credentials = userP.twitter_api.verify_credentials()
					if credentials:
						send_msg(userkey, 'Hi %s , from now on you can write your tweet and then it will be posted.'.decode('utf-8') % credentials['screen_name']  , response)
						userP.key = userP.twitter_api.token.key
						userP.secret = userP.twitter_api.token.secret
						userP.name = credentials['name']
						userP.screename = credentials['screen_name']
						userP.save()
						response.write('<goto=2>')
					else:
						send_msg(userkey,'Problems in authentication. Try again.',response)
						userP.delete()
						response.write('<goto=1>')
				else:
					#Checa se tem credenciais, entao twitta. (pequeno bug que contornei.)
					try:
						credentials = userP.twitter_api.verify_credentials()
						verbose = True
						if credentials:
							try:
								if len(msg) > 140:
									#Mensagens com mais de 140 caracteres tem q haver excecao.
									raise Exception()
								if msg.startswith('->'):
									verbose = False
									msg = msg[2:]
								resp = userP.twitter_api.tweet(msg.encode('utf-8'))
								#tudo ok
								resp  = simplejson.loads(resp)			
								if verbose:
									msg = 'Tweet sent successfuly: http://twitter.com/%s/statuses/%s' % (resp['user']['screen_name'], str(resp['id']))
									send_msg(userkey,msg,response)
								response.write('<goto=2>')
							except:
								#Problemas com o tweet.
								send_msg(userkey,'Problems in authentication or with the tweet(Remember: limit: 140 characters). Try again.'.decode('utf-8') ,response)
								response.write('<goto=2>')
						else:
							#Problemas com credenciais.
							send_msg(userkey,'I did not find the PINCODE or there was a failure during the authentication. Start over again.'.decode('utf-8') ,response)
							userP.delete()
							response.write('<goto=1>')
					except:
						#Problemas com credencial ou pincode .
						send_msg(userkey,'I did not find the PINCODE or there was a failure during the authentication. Start over again.'.decode('utf-8') ,response)
						userP.delete()
						response.write('<goto=1>')
			else:
				#VOlta para o estado inicial.
				response.write('<goto=1>')
						
		else:
			#Nao tem usuario no sistema, entao vamos comecar do zero.
			if step == 1:
				#avisa ao usuario que nao esta cadastrado.
				send_msg(userkey,'User still not registered. Please register your Twitter account to TweetTalk.'.decode('utf-8'),response)
				request_token = request.user.twitter_api.get_request_token(callback="oob")
				authorization_url = request.user.twitter_api.get_authorization_url(request_token)
				authorization_url = urllib.urlopen("http://tinyurl.com/api-create.php?url=%s" % urllib.quote(authorization_url)).read()
				send_msg(userkey,' Send me the PIN CODE provided by this link (After authentication): %s'.decode('utf-8') % authorization_url ,response)
				user, created = User.objects.get_or_create(userkey=userkey)
				user.userkey = userkey
				user.request_token = request_token.to_string()
				user.save()
				response.write('<goto=2>')
			else:
				#step inicial
				response.write('<goto=1>')
					
		
	return response 	
	