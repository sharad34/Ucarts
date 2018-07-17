from django import forms
#from django.forms import forms
from .models import Address

class AddressForm(forms.ModelForm):
	class Meta:
		model=Address 
		fields=[
		#'billing_profile',  		
		'address_line1',
		'address_line2',	
		#'address_type',
		'city',
		'postal_code',
		'state',
		'country',
		]
		#this will render exactly like in admin address import it in carts--views
