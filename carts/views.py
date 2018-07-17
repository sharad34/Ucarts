from django.shortcuts import render,redirect
from .models import Cart
from products.models import Product
from orders.models import Order
from accounts.forms import LoginForm  ,GuestForm
from billing.models import BillingProfile
from accounts.models import GuestEmail
from addresses.forms import AddressForm
from addresses.models import Address
from django.http import JsonResponse
from django.conf import settings


import stripe
STRIPE_SECRET_KEY = getattr(settings, "STRIPPE_SECRET_KEY","sk_test_vjtIDheLVZCAxiF01O2kwuxJ")
STRIPE_PUB_KEY     = getattr(settings, "STRIPPE_PUBLIC_KEY","pk_test_5txpgOEto3WbZjj7B2WpE1U3")
stripe_api_key     = STRIPE_SECRET_KEY



def cart_detail_api_view(request):
        cart_obj, new_obj=Cart.objects.new_or_get(request)
        products=[{
        "id":x.id,
        "url":x.get_absolute_url(),
        "name":x.name,
        "price":x.price
        }
        for  x in cart_obj.products.all()]#return a list like [<object>,<object>,<object>]..
        cart_data={"products":products,"subtotal":cart_obj.subtotal,"total":cart_obj.total}
        return JsonResponse(cart_data)#we have to turn the template type items to jsonresponse items

def cart_home(request):#we create an object
        cart_obj, new_obj=Cart.objects.new_or_get(request)
       
        return render(request,"carts/home.html",{"cart":cart_obj})



def cart_update(request):#we update the object
        product_id=request.POST.get('product_id')
        if product_id is not None:
            try:
              product_obj=Product.objects.get(id=product_id)
            except Product.DoesNotExist:
              return redirect("cart:home")        
            cart_obj,new_obj=Cart.objects.new_or_get(request)
            if product_obj in cart_obj.products.all():
                cart_obj.products.remove(product_obj)
                added=False
            else:
                cart_obj.products.add(product_obj)
                added=True 
            request.session['cart_items']=cart_obj.products.count() 
            if request.is_ajax():#Asynchronous JS or XML so we need to send either of it or JSON..JS Object Notation
                print("Ajax Request")
                json_data={
                "added":added,
                "removed":not added,
                "cartItemCount":cart_obj.products.count() #for updating the cart count in ajax
                }
                return JsonResponse(json_data,status=200)#status code added for error display 
                #return JsonResponse({"message":"Error 400"},status_code=400)used for check error Django Rest framework
        return redirect("cart:home")        

def checkout_home(request):
    cart_obj,cart_created=Cart.objects.new_or_get(request)
    if cart_created or cart_obj.products.count()==0:
        return redirect("cart:home")
    
        
    #user=request.user
    #billing_profile=None#commented after BillingProfile
    
    login_form=LoginForm()
    guest_form=GuestForm()
    address_form=AddressForm()
    billing_address_id=request.session.get("billing_address_id", None)#copy these and paste in addresses views
    shipping_address_id=request.session.get("shipping_address_id", None)

    #billing_address_form=AddressForm()#two instances on the same thing..now add to context


    order_obj=None
    
    billing_profile,billing_profile_created=BillingProfile.objects.new_or_get(request)#added after creating BillingManager 
    #now the below is that is before  if billing_profile is not None: is donw for selecting address procedure
    #shipping_address_qs           =address_qs.filter(address_type='shipping')
    #billing_address_qs            =address_qs.filter(address_type='billing')
    address_qs=None#add in context
    has_card  =False        
    if billing_profile is not None:

        if request.user.is_authenticated(): 
            address_qs=Address.objects.filter(billing_profile=billing_profile)
        order_obj, order_obj_created=Order.objects.new_or_get(billing_profile, cart_obj)
        if shipping_address_id:
            order_obj.shipping_address=Address.objects.get(id=shipping_address_id)
            del request.session["shipping_address_id"]
        if billing_address_id:
            order_obj.billing_address=Address.objects.get(id=billing_address_id)
            del request.session["billing_address_id"]
        if billing_address_id or shipping_address_id:
            order_obj.save()
        has_card = billing_profile.has_card    

    if request.method=="POST":
        "some kind of check"
        is_prepared=order_obj.check_done()
        if is_prepared:

            did_charge, crg_msg  =  billing_profile.charge(order_obj)
        #update the order_obj
            if did_charge: 
                order_obj.mark_paid()
                request.session['cart_items']= 0 
                del request.session['cart_id']
                if not billing_profile.user:
                    billing_profile.set_cards_inactive()
                return redirect("cart:success")

            else:
                print(crg_msg)
                return redirect("cart:checkout")

                  
    '''
    so now we need to delete the session id del request.session['cart_id']
    and update the order_obj to done or paid
    and redirect to some succes page

    '''        
    #below is commented till order_obj, oredr_obj_created=Order.objects.new_or_get(billing_profile, cart_obj) after createing BillingProfileManager
    #guest_email_id=request.session.get('guest_email_id')
    #if user.is_authenticated():
     #    'logged in user checkout..remembers payment stuff'
      #   billing_profile,billing_profile_created=BillingProfile.objects.get_or_create(user=user,email=user.email)
    #elif guest_email_id is not None:
     #    ' guest checkout..auto reloads payment stuff'
      #   guest_email_obj=GuestEmail.objects.get(id=guest_email_id)
       #  billing_profile,billing_guest_profile_created=BillingProfile.objects.get_or_create(email=guest_email_obj.email)
    #else:
     #    pass

    #if billing_profile is not None:
     #   order_obj, oredr_obj_created=Order.objects.new_or_get(billing_profile, cart_obj)#added after creating the OrderManager and doing objects=OrderManager()
        #below code is commented after this


        #order_qs=Order.objects.filter(billing_profile=billing_profile, cart=cart_obj, active=True)
        #if order_qs.count()==1:

         #   order_obj=order_qs.first()
        #else:
            #below is done to stop the cart from changing..active and non active
    '''
         below is commeneted after adding this in orders.models  qs=Oreder.objects.filter(cart=instance.cart).exclude(billing_profile=instance.billing_profile)
    if qs.exists():
        qs.update(active=False);
   
         old_order_qs=Order.objects.exclude(billing_profile=billing_profile).filter(cart=cart_obj)
            if old_order_qs.exists():
                print("yesss")
                old_order_qs.update(active=False)'''
         
         #   order_obj=Order.objects.create(billing_profile=billing_profile, cart=cart_obj)
            
         


    #order_obj=None
    context={
        
        "billing_profile":billing_profile,
        "login_form":login_form,
        "guest_form":guest_form,
        "object":order_obj,
        "address_form":address_form,
        "address_qs":address_qs,
        "has_card":has_card,
        "publish_key":STRIPE_PUB_KEY# we have this publish key in payment method view

     #   "billing_address_form":billing_address_form,
    }        
    return render(request,"carts/checkout.html",context)        

def checkout_done_view(request):
    return render(request, "carts/checkout-done.html", {} )