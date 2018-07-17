# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
# Create your models here.
#when a user registers he will have a BillingProfile
from billing.models import BillingProfile
#we can have many different addreses for a billingprofile


ADDRESS_TYPES=(
	('billing', 'Billing'),
	('shipping', 'Shipping'),
	)


class Address(models.Model):
	billing_profile         =models.ForeignKey(BillingProfile)
	address_line1           =models.CharField(max_length=120)
	address_line2           =models.CharField(max_length=120, null=True, blank=True)
	address_type            =models.CharField(max_length=120, choices=ADDRESS_TYPES)
	city                    =models.CharField(max_length=120)
	state                   =models.CharField(max_length=120)
	postal_code             =models.CharField(max_length=120)
	country                 =models.CharField(max_length=120, default='India')

	def __str__(self):
		return str(self.billing_profile)#billingprofilemodel str return email

	def get_address(self):#created to give address at finalize checkout
		return "{line1}\n{line2}\n{city}\n{state} {postal}\n{country}".format(
			line1=self.address_line1,
			line2=self.address_line2 or "",
			city=self.city,
			state=self.state,
			postal=self.postal_code,
			country=self.country
			)	

# now we have to create a form to handle these addresses