from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import AnonRateThrottle
from .models import Organization,Service,Opportunity,Inquiry
from .serializers import ServiceSerializer,OpportunitySerializer,InquirySerializer

class PublicServices(generics.ListAPIView):
    permission_classes=[permissions.AllowAny]
    serializer_class=ServiceSerializer
    def get_queryset(self):
        return Service.objects.filter(organization__slug=self.kwargs['slug'],published=True).order_by('-created_at')

class PublicOpportunities(generics.ListAPIView):
    permission_classes=[permissions.AllowAny]
    serializer_class=OpportunitySerializer
    def get_queryset(self):
        return Opportunity.objects.filter(organization__slug=self.kwargs['slug'],published=True,verified_by__isnull=False).order_by('-created_at')

class InquiryThrottle(AnonRateThrottle):
    rate='5/hour'

class SubmitInquiry(APIView):
    permission_classes=[permissions.AllowAny]
    throttle_classes=[InquiryThrottle]
    def post(self,request,slug):
        org=get_object_or_404(Organization,slug=slug)
        serializer=InquirySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service=serializer.validated_data.get('service')
        if service and (service.organization_id!=org.id or not service.published):
            return Response({'service':['Invalid service']},status=400)
        Inquiry.objects.create(organization=org,**serializer.validated_data)
        return Response({'message':'Inquiry received'},status=status.HTTP_201_CREATED)

class Health(APIView):
    permission_classes=[permissions.AllowAny]
    def get(self,request): return Response({'status':'ok','app':'Ehan International Ltd'})
