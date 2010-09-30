#-*- coding:utf-8 -*-

from django.http import HttpResponse
#from twitterauth.decorators import login_required
from twitterauth.models import User
import base64
import httplib
import urllib
import re
from twitterauth import oauth

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
		 	if step == 2:
				#recebe o pincode
				pattern = re.compile("\\d{7}")
				result = re.findall(pattern,msg)
				if result:
					#tem algum PINCODE, pega o PINCODE
					userP.twitter_api.token = request.user.twitter_api.get_access_token(oauth.OAuthToken.from_string(userP.request_token), verifier=result[0])
					credentials = userP.twitter_api.verify_credentials()
					if credentials:
						send_msg(userkey, 'Olá %s , a partir de agora você poderá escrever seu tweet e ele será postado no seu Twitter. '.decode('utf-8') % credentials['screen_name']  , response)
						userP.key = userP.twitter_api.token.key
						userP.secret = userP.twitter_api.token.secret
						userP.name = credentials['name']
						userP.screename = credentials['screen_name']
						userP.save()
						response.write('<goto=3>')
					else:
						send_msg(userkey,'Problemas na autenticacao. Tente outra vez.',response)
						userP.delete()
						response.write('<goto=1>')
				else:
					#So ruido.
					send_msg(userkey,'Não encontrei o PINCODE ou houve falha na autenticação, comece novamente.'.decode('utf-8') ,response)
					response.write('<goto=1>')
			elif step == 3:
				#Agora so tweetar.
				userP.twitter_api.tweet(msg)
				response.write('<goto=3>')
			elif step == 1:
				#Primeira vez que chegou vamos ver o que fazer
				credentials = userP.twitter_api.verify_credentials()
				if credentials:
					send_msg(userkey, 'Olá %s , a partir de agora você poderá escrever seu tweet e ele será postado no seu Twitter. '.decode('utf-8') % credentials['screen_name']  , response)
					userP.name = credentials['name']
					userP.screename = credentials['screen_name']
					userP.save()
					response.write('<goto=3>')
				else:
					send_msg(userkey,'Problemas na autenticacao. Tente outra vez.',response)
					userP.delete()
					response.write('<goto=1>')
					
					
			else:
				send_msg(userkey,'stepInside:'+str(step),response)
				response.write('<goto=1>')
					
		else:
			#Nao tem usuario no sistema, entao vamos comecar do zero.
			if step == 1:
				#avisa ao usuario que nao esta cadastrado.
				send_msg(userkey,'Usuário não cadastrado. Favor cadastrar sua conta ao TweetTalk no Twitter.'.decode('utf-8'),response)
				request_token = request.user.twitter_api.get_request_token(callback="oob")
				authorization_url = request.user.twitter_api.get_authorization_url(request_token)
				authorization_url = urllib.urlopen("http://tinyurl.com/api-create.php?url=%s" % urllib.quote(authorization_url)).read()
				send_msg(userkey,' Me informe o PIN CODE fornecido por este link (Após autenticação): %s'.decode('utf-8') % authorization_url ,response)
				user, created = User.objects.get_or_create(userkey=userkey)
				user.userkey = userkey
				user.request_token = request_token.to_string()
				user.save()
				response.write('<goto=2>')
			else:
				send_msg(userkey,'stepUser:'+str(step),response)
				response.write('<goto=1>')
					

	#if step == 0:
	#	x = send_msg(userkey,msg)
	#	return x
	#else:
	#	response.write('indo para o 2')
	#	response.write('<goto=2>')					
	return response
		
	
	#return HttpResponse(authorization_url)
	
	