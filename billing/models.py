from django.db import models
from django.db.models.signals import post_save, pre_save
from django.conf import settings
from accounts.models import GuestEmail
from django.core.urlresolvers import reverse
#from accounts.models import BillingProfile

import stripe
stripe.api_key="sk_test_vjtIDheLVZCAxiF01O2kwuxJ"

User=settings.AUTH_USER_MODEL

#FIXTURES helps us to save the existing db contents clean up the db and add new db content for models apps etc.



#def billing_profile_created_receiver(sender,instance,created,*args,**kwargs):
    #if created:
        #print("Send to stripe/braintree")
        #instance.customer_id=newID
        #instance.save()
class BillingProfileManager(models.Manager):
    def new_or_get(self, request):
        user=request.user
        guest_email_id=request.session.get('guest_email_id')
        created=False
        obj=None
        if user.is_authenticated():
            'logged in user checkout..remembers payment stuff'
            obj,created=self.model.objects.get_or_create(
                user=user,
                email=user.email
                )
        elif guest_email_id is not None:
            'guest checkout..auto reloads payment stuff'
            guest_email_obj=GuestEmail.objects.get(id=guest_email_id)
            obj,created=self.model.objects.get_or_create(
                email=guest_email_obj.email
                )
        else:
            pass
        return obj, created    
#in above billing_profile has been named as obj and BillingProfile is now simply self.model


class BillingProfile(models.Model):
    user=models.OneToOneField(User,null=True,blank=True)
    email=models.EmailField()
    active=models.BooleanField(default=True)
    updated=models.DateTimeField(auto_now=True)
    timestamp=models.DateTimeField(auto_now_add=True)
    customer_id=models.CharField(max_length=120, null=True, blank=True)
    #customer_id in stripe or braintree


    objects=BillingProfileManager()
   

    def __str__(self):
        return self.email

    def charge(self, order_obj, card=None):
        return Charge.objects.do(self, order_obj, card) 
#..............................way to see if cards exists.......................
    def get_cards(self):
        return self.card_set.all()     


    @property     
    def has_card(self):#used for reverse relaitionships...instance.has_card
        #instance=self
        card_qs =self.get_cards()
        return card_qs.exists() #True or False   

    @property
    def default_card(self):
        default_cards=self.get_cards().filter(active=True, default=True)#add defaultcard in checkout.html.<p>Order Total: {{ object.total }}</p>     
        if default_cards.exists():
            return default_cards.first()
        return None         
        #add has_card in carts views
#...............................................................................

    def set_cards_inactive(self):
        cards_qs = self.get_cards()
        cards_qs.update(active=False)
        return cards_qs.filter(active=True).count()

    def get_payment_method_url(self):
        return reverse('billing-payment-method')

def billing_profile_created_receiver(sender, instance, *args, **kwargs):
    if not instance.customer_id and instance.email:
        print("ACTUAL API REQUEST SEND TO STRIPE/BRAINTREE")
        customer=stripe.Customer.create(
            email=instance.email,
            )
        print(customer)
        instance.customer_id=customer.id

pre_save.connect(billing_profile_created_receiver, sender=BillingProfile)      


def user_created_receiver(sender,instance,created,*args,**kwargs):
    if created and instance.email:
        BillingProfile.objects.get_or_create(user=instance,email=instance.email)

post_save.connect(user_created_receiver,sender=User)        



# <Card card id=card_1CnKZqE1GlRKQWPGBdfYlXmd at 0x00000a> JSON: {
#   "id": "card_1CnKZqE1GlRKQWPGBdfYlXmd",
#   "object": "card",
#   "address_city": null,
#   "address_country": null,
#   "address_line1": null,
#   "address_line1_check": null,
#   "address_line2": null,
#   "address_state": null,
#   "address_zip": null,
#   "address_zip_check": null,
#   "brand": "Visa",
#   "country": "US",
#   "customer": "cus_DDm8XfVJ60DC23",
#   "cvc_check": null,
#   "dynamic_last4": null,
#   "exp_month": 8,
#   "exp_year": 2019,
#   "fingerprint": "Uzad0svwUIX6RQye",
#   "funding": "credit",
#   "last4": "4242",
#   "metadata": {
#   },
#   "name": null,
#   "tokenization_method": null
# }


class CardManager(models.Manager):

    def all(self, *args, **kwargs):#override cardmanager ....Modelclass.objects.all()
        return self.get_queryset().filter(active=True)

    def add_new(self, billing_profile, token):
        if token:
            customer        =   stripe.Customer.retrieve(billing_profile.customer_id)#taken from https://stripe.com/docs/api/python#create_card
            stripe_card_response   =   customer.sources.create(source=token)
            new_card=self.model(
                billing_profile=billing_profile,
                stripe_id=stripe_card_response.id,
                brand=stripe_card_response.brand,
                country=stripe_card_response.country,
                exp_month=stripe_card_response.exp_month,
                exp_year=stripe_card_response.exp_year,
                last4=stripe_card_response.last4
                )
            new_card.save() 
            return new_card
        return None            



class Card(models.Model):
    billing_profile =   models.ForeignKey(BillingProfile)
    stripe_id       =   models.CharField(max_length=120)
    brand           =   models.CharField(max_length=120, null=True, blank=True)
    country         =   models.CharField(max_length=20, null=True, blank=True)
    exp_month       =   models.IntegerField(null=True, blank= True)
    exp_year        =   models.IntegerField(null=True, blank= True)
    last4           =   models.CharField(max_length=4, null=True, blank=True)
    default         =   models.BooleanField(default=True)
    active          =   models.BooleanField(default=True)
    timestamp       =   models.DateTimeField(auto_now_add=True)

    objects= CardManager()


    def __str__(self):
        return "{} {}".format(self.brand,self.last4)


class ChargeManager(models.Manager):
    def do(self, billing_profile, order_obj, card=None):#order_obj get from orders app Orde 
        card_obj=card
        if card_obj is None:
            cards=billing_profile.card_set.filter(default=True)
            if cards.exists():
                card_obj = cards.first()
        if card_obj is None: 
            return False, "No cards Available"                     

        c  = stripe.Charge.create(
            amount=int(order_obj.total*100),
            currency="usd",
            customer=billing_profile.customer_id,#BillingProfile.objects.filter(email='sharad12@gmail.com').first().stripe_id,
            source=card_obj.stripe_id,#Card.objects.filter(billing_profile_email='sharad12@gmail.com').first().stripe_id,
            metadata={"order_id":order_obj.order_id},
            #order_id=order_id,
             )
            
        new_charge_obj = self.model(
                billing_profile          =billing_profile,
                stripe_id                =c.id,
                paid                     =c.paid,
                refunded                 =c.refunded,
                outcome                  =c.outcome,
                outcome_type             =c.outcome['type'],
                seller_message           =c.outcome.get('seller message'),
                risk_level               =c.outcome.get('risk_level'),      

            )
        new_charge_obj.save()
        return new_charge_obj.paid, new_charge_obj.seller_message      


class Charge(models.Model):
   billing_profile          =models.ForeignKey(BillingProfile)
   stripe_id                =models.CharField(max_length=120) 
   paid                     =models.BooleanField(default=False)
   refunded                 =models.BooleanField(default=False)
   outcome                  =models.TextField(null=True, blank=True)
   outcome_type             =models.CharField(max_length=120, null=True, blank=True)
   seller_message           =models.CharField(max_length=120, null=True, blank=True)
   risk_level               =models.CharField(max_length=120,null=True,blank=True)


   objects=ChargeManager()

#post save method for the new card added

def new_card_post_save_receiver(sender, instance, created, *args, **kwargs):
    if instance.default:#instance is true so this will run for sure for first time
        billing_profile = instance.billing_profile
        qs= Card.objects.filter(billing_profile=billing_profile).exclude(pk=instance.pk)
        qs.update(default=False)

post_save.connect(new_card_post_save_receiver,sender=Card)
