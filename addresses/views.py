# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.http import is_safe_url
from django.shortcuts import render, redirect
from .forms import AddressForm
from billing.models import BillingProfile
from .models import Address
# Create your views here.

#view created after shipping address form done in form.html and addresses.forms

def checkout_address_create_view(request):
    form = AddressCheckoutForm(request.POST or None)
    context = {
        "form": form
    }
    next_ = request.GET.get('next')
    next_post = request.POST.get('next')
    redirect_path = next_ or next_post or None
    if form.is_valid():
        print(request.POST)
        instance = form.save(commit=False)
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
        if billing_profile is not None:
            address_type = request.POST.get('address_type', 'shipping')
            instance.billing_profile = billing_profile
            instance.address_type = address_type
            instance.save()
            request.session[address_type + "_address_id"] = instance.id
            print(address_type + "_address_id")
        else:
            print("Error here")
            return redirect("cart:checkout")

        if is_safe_url(redirect_path, request.get_host()):
            return redirect(redirect_path)
    return redirect("cart:checkout") 


def checkout_address_reuse_view(request):
    if request.user.is_authenticated():
        context = {}
        next_ = request.GET.get('next')
        next_post = request.POST.get('next')
        redirect_path = next_ or next_post or None
        if request.method == "POST":
            print(request.POST)
            shipping_address = request.POST.get('shipping_address', None)
            address_type = request.POST.get('address_type', 'shipping')
            billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
            if shipping_address is not None:
                qs = Address.objects.filter(billing_profile=billing_profile, id=shipping_address)
                if qs.exists():
                    request.session[address_type + "_address_id"] = shipping_address
                if is_safe_url(redirect_path, request.get_host()):
                    return redirect(redirect_path)
    return redirect("cart:checkout") 



















# def checkout_address_create_view(request):#now import it in urls..
# 	form=AddressForm(request.POST or None)
# 	context={
# 		"form":form
# 	}
# 	next_=request.GET.get('next')
#   	next_post=request.POST.get('next')
#   	redirect_path=next_ or next_post or None

#   	if form.is_valid():									
#   		print(request.POST)
#   		instance=form.save(commit=False)

#  		billing_profile,billing_profile_created=BillingProfile.objects.new_or_get(request)
#  		if billing_profile is not None:
#  			address_type=request.POST.get('address_type','shipping')

# 	  		instance.billing_profile=billing_profile
# 	  		instance.address_type=address_type
# 	  		instance.save()

# 	  		request.session[address_type +"_address_id"]=instance.id
# 	  		print(address_type +"_address_id")		
	  		
    		
#   		else:
#   			print("error here")
#   			return redirect("cart:checkout")
#   		if is_safe_url(redirect_path,request.get_host()):
#   			return redirect(redirect_path)
# 	return redirect("cart:checkout")#we need to return a redirect so copy the guest_register_view bec it is similar


# def checkout_address_reuse_view(request):#now import it in urls..
# 	if request.user.is_authenticated():
# 		next_=request.GET.get('next')
# 	  	next_post=request.POST.get('next')
# 	  	redirect_path=next_ or next_post or None
# 	  	if request.method=="POST":
# 	  		print(request.POST)
# 	  		shipping_address=request.POST.get('shipping_address',None)
# 	 		address_type=request.POST.get('address_type','shipping')

# 	  		billing_profile,billing_profile_created=BillingProfile.objects.new_or_get(request)
# 	  		#to get the actual session item
# 		  	if shipping_address is not None:	
# 		  		qs=Address.objects.filter(billing_profile=billing_profile,id =shipping_address)
# 		  		if qs.exists():
# 		  			request.session[address_type +"_address_id"]=shipping_address		
		  

# 	  			if is_safe_url(redirect_path,request.get_host()):
# 	  				return redirect(redirect_path)
# 	return redirect("cart:checkout")#we need to return a redirect so copy the guest_register_view bec it is similar




'''
	def guest_register_view(request):
    form=AddressForm(request.POST or None)
    context={
        "form":form
    }
    next_=request.GET.get('next')
    next_post=request.POST.get('next')
    redirect_path=next_ or next_post or None

    if form.is_valid():
        email=form.cleaned_data.get("email")
        new_guest_email=GuestEmail.objects.create(email=email)
        request.session['guest_email_id']=new_guest_email.id
        if is_safe_url(redirect_path,request.get_host()):
                return redirect(redirect_path)
        else:    
                return redirect("/register/")
        
    return redirect("/register/")


'''