from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.utils.http import is_safe_url
# Create your views here.

from .models import BillingProfile, Card
from django.conf import settings


import stripe
STRIPE_SECRET_KEY = getattr(settings, "STRIPPE_SECRET_KEY","sk_test_vjtIDheLVZCAxiF01O2kwuxJ")
STRIPE_PUB_KEY     = getattr(settings, "STRIPPE_PUBLIC_KEY","pk_test_5txpgOEto3WbZjj7B2WpE1U3")
stripe_api_key	   = STRIPE_SECRET_KEY

def payment_method_view(request):
	# if request.user.is_authenticated():
	# 	billing_profile=request.user.billingprofile
	# 	customer_id=billing_profile.customer_id#this is all i need from stripe stuff
	# 	#go to carts and check for billingprofiles

	billing_profile,billing_profile_created=BillingProfile.objects.new_or_get(request)	
	if not billing_profile:
		return redirect("/cart")
		
	next_url=None
	next_=request.GET.get('next')#http://127.0.0.1:8000/billing/payment-method/?next=/billing/
	print("method_view")
	print(next_)
	if is_safe_url(next_,request.get_host()):
		               
		next_url=next_

	return render(request, 'billing/payment-method.html', {"publish_key":STRIPE_PUB_KEY,
		"next_url":next_url}
		)	


def payment_method_createview(request):
	if request.method =="POST" and request.is_ajax():
		billing_profile,billing_profile_created=BillingProfile.objects.new_or_get(request)
		if not billing_profile:
			return HttpResponse({"message":"Cannot Find This User"}, status_code=401)		
		print(request.POST)

		token=request.POST.get('token')#this should create a cust card based on this token
		if token is not None:#check if name is token in stripetokenhandle in ecommercemain.js
			# customer 		= 	stripe.Customer.retrieve(billing_profile.customer_id)#taken from https://stripe.com/docs/api/python#create_card
			# card_response	=	customer.sources.create(source=token)
			# #new_card_obj	= 	Card.objects.add_new(billing_profile, card_response)
			new_card_obj	= 	Card.objects.add_new(billing_profile, token)
			print(new_card_obj)#start saving our cards too

		return JsonResponse({"message":"Success ! Your Card Was Added."})
	return HttpResponse("error", status_code=401) 