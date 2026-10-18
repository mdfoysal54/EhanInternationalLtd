from django.urls import path
from . import views
urlpatterns=[
 path('<slug:slug>/customers/',views.customers,name='office-customers'),
 path('<slug:slug>/cases/',views.cases,name='office-cases'),
 path('<slug:slug>/cases/<uuid:pk>/',views.case_detail,name='office-case'),
 path('<slug:slug>/cases/<uuid:pk>/upload/',views.upload,name='office-upload'),
 path('<slug:slug>/documents/<uuid:pk>/download/',views.download,name='office-download'),
]