from django.db import models
from django.contrib.auth.models import(
		AbstractBaseUser,#this is the class we will use for implementing our own user model
		BaseUserManager
	) 


# Create your models here.

class UserManager(BaseUserManager):#we have to create and add it in the settings auth_user_model
	def create_user(self, email,full_name=None, password=None,is_active=True, is_staff=False, is_admin=False):
		if not email:
			raise ValueError("Users must have an Email")
		if not password:
			raise ValueError("Users must have a Password")
		#if not full_name:
		#	raise ValueError("Users must have a full_name")
		user_obj = self.model(
			email=self.normalize_email(email),
			full_name=full_name 

		)	
		user_obj.set_password(password) #change user password
		user_obj.staff		=is_staff
		user_obj.admin		=is_admin
		user_obj.active		=is_active
		user_obj.save(using=self._db)
		return user_obj

	def create_staffuser(self, email, full_name=None, password=None):
		user = self.create_user(
				email,
				full_name=full_name,
				password=password,
				is_staff=True
			)	
		return user

	def create_superuser(self, email,full_name=None, password=None):
		user = self.create_user(
				email,
				full_name=full_name,
				password=password,
				is_staff=True,
				is_admin=True
			)	
		return user
	

class User(AbstractBaseUser):#custom user class
	email    			=models.EmailField(max_length=255, unique=True)
	full_name  			=models.CharField(max_length=255, blank=True, null=True)
	active				=models.BooleanField(default=True)#can login
	staff				=models.BooleanField(default=True)#staff user
	admin				=models.BooleanField(default=True)#superuser
	timestamp			=models.DateTimeField(auto_now_add=True)

	USERNAME_FIELD	= 'email'#username
	#USERNAME and password are req by default
	REQUIRED_FIELDS = []#['full_name']

	objects=UserManager()

	def __str__(self):
		return self.email

	def get_full_name(self):
		if self.full_name:
			return self.full_name
		return self.email

	def get_short_name(self):
		return self.email

	def has_perm(self, perm, obj=None): #we need to def these perms when a new custom model and db is created..that is giving permissions
		return True

	def has_module_perms(self, app_label):
		return True		

	@property
	def is_staff(self):
		return self.staff

	@property
	def is_admin(self):
		return self.admin

	@property
	def is_active(self):
		return self.active 


class GuestEmail(models.Model):
	email 				=models.EmailField()
	active				=models.BooleanField(default=True)
	updated				=models.DateTimeField(auto_now=True)
	timestamp			=models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.email

    
    	

