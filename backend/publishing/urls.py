from django.urls import path
from . import views
urlpatterns=[path('<slug:slug>/',views.public_site,name='ehan-public'),path('<slug:slug>/portal/',views.client_portal,name='ehan-client-portal')]
