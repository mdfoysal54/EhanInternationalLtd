from django.urls import path
from .api import CustomerListCreate, OrderListCreate, CaseList, AdvanceCase

urlpatterns = [
    path('<slug:slug>/customers/', CustomerListCreate.as_view()),
    path('<slug:slug>/orders/', OrderListCreate.as_view()),
    path('<slug:slug>/cases/', CaseList.as_view()),
    path('<slug:slug>/cases/<uuid:case_id>/advance/', AdvanceCase.as_view()),
]