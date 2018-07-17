from django.shortcuts import render,get_object_or_404
from django.views.generic import ListView,DetailView
from .models import Product
from carts.models import Cart
from django.http import Http404
from analytics.mixins import ObjectViewedMixin#used in productdetailslugview where the obj will be viewed
# Create your views here.

class ProductFeaturedListView(ListView):
    template_name="products/list.html"

    def get_queryset(self,*args,**kwargs):
        request=self.request
        return Product.objects.featured()

class ProductFeaturedDetailView(ObjectViewedMixin, DetailView):
    queryset=Product.objects.featured()
    template_name="products/featured-detail.html"

    #def get_queryset(self,*args,**kwargs):
        #request=self.request
        #return Product.objects.all()


class ProductListView(ListView):
    queryset=Product.objects.all()
    template_name="products/list.html"

    def get_context_data(self,*args,**kwargs):
        context=super(ProductListView,self).get_context_data(*args,**kwargs)
        request=self.request
        cart_obj,new_obj=Cart.objects.new_or_get(request)
        context['cart']=cart_obj
        return context

    #def get_context_data(self,*args,**kwargs):
        #context=super(ProductListView,self).get_context_data(*args,**kwargs)
        #return context
    
    def get_queryset(self,*args,**kwargs):
        request=self.request
        return Product.objects.all()

def product_list_view(request):
    queryset=Product.objects.all()
    context={
        'object_list':queryset
    }
    return render(request,"products/list.html",context)



class ProductDetailSlugView(ObjectViewedMixin, DetailView):
    queryset=Product.objects.all()
    template_name="products/detail.html"
    
    def get_context_data(self,*args,**kwargs):
        context=super(ObjectViewedMixin,self).get_context_data(*args,**kwargs)
        request=self.request
        cart_obj,new_obj=Cart.objects.new_or_get(request)
        context['cart']=cart_obj
        return context

    def get_object(self,*args,**kwargs):
        request=self.request
        slug=self.kwargs.get('slug')
        #instance=get_object_or_404(Product,slug=slug,active=True)
        #if instance is None:
           #raise Http404("Product Doesn't exist")
        try:
            instance=Product.objects.get(slug=slug,active=True)
        except Product.DoesNotExist:
            raise Http404("Not found...")
        except Product.MultipleObjectsReturned:
            qs=Product.objects.filter(slug=slug,active=True)
            instance=qs.first()
        except:
            raise Http404("Not")        
        #object_viewed_signal.send(instance.__class__, instance=instance, request=request)#this is the actual sender...
        #we dont have to be too redundant so we will create a mixin instead of this.      
        return instance
    




class ProductDetailView(ObjectViewedMixin, DetailView):
    #queryset=Product.objects.all()
    template_name="products/detail.html"


    #def get_context_data(self,*args,**kwargs):
        #context=super(ProductDetailView,self).get_context_data(*args,**kwargs)
        #return context
    
    
    def get_object(self,*args,**kwargs):
        request=self.request
        pk=self.kwargs.get('pk')
        instance=Product.objects.get_by_id(pk)
        if instance is None:
           raise Http404("Product Doesn't exist")
        return instance
    
    #def get_queryset(self,*args,**kwargs):
        #request=self.request
        #pk=self.kwargs.get('pk')
        #return Product.objects.filter(pk=pk)


def product_detail_view(request,pk=None,*args,**kwargs):
    #instance=Product.objects.get(pk=pk)
    #instance=get_object_or_404(Product,pk=pk)
    #try:
        #instance=Product.objects.get(id=pk)
    #except:
        #print("no product here")
        #raise Http404("Product Doesn't exist")
    #except:
        #print("huh")  
    


    instance=Product.objects.get_by_id(pk)
    if instance is None:
        raise Http404("Product Doesn't exist")
  
  
  
  
   # qs=Product.objects.filter(id=pk)
    #if qs.exists() and qs.count()==1:
     #   instance=qs.first()
    #else:
        #raise Http404("Product Doesn't exist")              
   
   
    context={
        "object":instance
    }    
    return render(request,"products/detail.html",context)