from django.urls import path
from . import views

urlpatterns = [
    path('<slug:slug>/', views.dashboard, name='agency-workspace'),
    path('<slug:slug>/customers/', views.customer_list, name='erp-customers'),
    path('<slug:slug>/customers/new/', views.customer_create, name='erp-customer-new'),
    path('<slug:slug>/customers/<uuid:pk>/edit/', views.customer_edit, name='erp-customer-edit'),
    path('<slug:slug>/cases/', views.case_list, name='erp-cases'),
    path('<slug:slug>/tasks/', views.task_list, name='erp-tasks'),
    path('<slug:slug>/tasks/<uuid:pk>/complete/', views.task_complete, name='erp-task-complete'),
]