from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.cart),
    url(r'^add$', views.add),
    url(r'^edit$', views.edit),
    url(r'^delete$', views.delete),
]