from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from .models import Organization,Service,Inquiry,Opportunity
from django.contrib.auth import get_user_model
class PublicIsolationTests(TestCase):
    def setUp(self):
        self.a=Organization.objects.create(name='Ehan International Ltd',slug='ehan-international')
        self.b=Organization.objects.create(name='Other Agency',slug='other-agency')
        Service.objects.create(organization=self.a,title='Tour package',slug='tour',category='Tourism',published=True)
        Service.objects.create(organization=self.b,title='Other private',slug='other',category='Other',published=True)
        self.client=APIClient()
    def test_public_services_tenant_scoped(self):
        r=self.client.get('/api/v1/public/ehan-international/services/')
        self.assertEqual(r.status_code,200)
        self.assertEqual(len(r.data['results']) if isinstance(r.data,dict) else len(r.data),1)
    def test_inquiry_requires_consent(self):
        r=self.client.post('/api/v1/public/ehan-international/inquiries/',{'name':'A','phone':'123','message':'Hello','consent':False},format='json')
        self.assertEqual(r.status_code,400)
    def test_inquiry_created(self):
        r=self.client.post('/api/v1/public/ehan-international/inquiries/',{'name':'A','phone':'123','message':'Hello','consent':True},format='json')
        self.assertEqual(r.status_code,201)
        self.assertEqual(Inquiry.objects.count(),1)
    def test_unverified_opportunity_not_public(self):
        Opportunity.objects.create(organization=self.a,title='Job',country='Saudi Arabia',published=True)
        r=self.client.get('/api/v1/public/ehan-international/opportunities/')
        self.assertEqual(len(r.data),0)
