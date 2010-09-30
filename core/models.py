from django.db import models

# Create your models here.
class UserTalk(models.Model):
	username = models.CharField(max_length=200)
	userkey = models.CharField(max_length=255,  primary_key=True)
	token = models.TextField()
	twitter_username = models.TextField()
	is_valid = models.BooleanField()
	date = models.DateTimeField(auto_now_add = True)