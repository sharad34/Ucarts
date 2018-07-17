
from django.conf.urls import url
from django.contrib import admin
from products.views import (ProductListView,
                            #ProductDetailView,
                            #product_detail_view,
                            #product_list_view,
                            #ProductFeaturedListView,
                            #ProductFeaturedDetailView,
                            ProductDetailSlugView)
                            


urlpatterns = [
    url(r'^$',ProductListView.as_view(),name='list'),
    url(r'^(?P<slug>[\w-]+)/$',ProductDetailSlugView.as_view(),name='detail'),
    
    
]

