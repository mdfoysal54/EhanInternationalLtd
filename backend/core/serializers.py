from rest_framework import serializers
from .models import Service,Opportunity,Inquiry
class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model=Service
        fields=['id','title','slug','category','description','price_from','currency']
class OpportunitySerializer(serializers.ModelSerializer):
    class Meta:
        model=Opportunity
        fields=['id','title','country','description','employer','vacancies','deadline']
class InquirySerializer(serializers.ModelSerializer):
    class Meta:
        model=Inquiry
        fields=['name','email','phone','message','consent','service']
    def validate_consent(self,value):
        if not value: raise serializers.ValidationError('Consent is required')
        return value
