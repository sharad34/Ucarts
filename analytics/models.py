# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings 

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from .signals import object_viewed_signal#a rec func need to be created for this 
from .utils import get_client_ip

# Create your models here.

User = settings.AUTH_USER_MODEL#allows us to set the user model whether its a custom user or not

class ObjectViewed(models.Model):
	user 			=models.ForeignKey(User, blank=True, null=True)# User instance..instance.id
	ip_address		=models.CharField(max_length=220, blank=True, null=True)# there is an IP field but here not used to not worry about validators
	content_type	=models.ForeignKey(ContentType) # User, Product, Order, Cart, Address
	object_id 		=models.PositiveIntegerField() # User id ,Product id, Cart id.....
	content_object	=GenericForeignKey('content_type','object_id') # Product instance
	timestamp		=models.DateTimeField(auto_now_add=True)	

	def __str__(self):
		return "%s viewed on %s"%(self.content_object, self.timestamp)	


	class Meta:
		ordering = ['-timestamp'] #most recent saved show up first
		verbose_name = 'Object viewed'
		verbose_name_plural = 'Objects viewed'	


def object_viewed_receiver(sender, instance, request, *args, **kwargs):
	
	c_type=ContentType.objects.get_for_model(sender)#same as instance__class__
	print(sender)
	print(instance)
	print(request)
	print(request.user)		
	new_view_obj=ObjectViewed.objects.create(
		request=request.user,
		object_id=instance.id,
		content_type=c_type,
		ip_address=get_client_ip(request)
		)

object_viewed_signal.connect(object_viewed_receiver)
	