from django.urls import path
from .views import Health,PublicServices,PublicOpportunities,SubmitInquiry
urlpatterns=[
    path('health/',Health.as_view()),
    path('public/<slug:slug>/services/',PublicServices.as_view()),
    path('public/<slug:slug>/opportunities/',PublicOpportunities.as_view()),
    path('public/<slug:slug>/inquiries/',SubmitInquiry.as_view()),
]
