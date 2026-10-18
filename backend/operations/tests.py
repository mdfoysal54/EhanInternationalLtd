from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from core.models import Organization, Membership
from .models import Customer, ServiceOrder, WorkflowTemplate, WorkflowStage, Case


class TenantOperationsTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='agency_owner', password='test-password-123')
        self.a = Organization.objects.create(name='Agency A', slug='agency-a')
        self.b = Organization.objects.create(name='Agency B', slug='agency-b')
        Membership.objects.create(user=self.user, organization=self.a, role='owner')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_customer_isolation(self):
        Customer.objects.create(organization=self.b, name='Private B')
        response = self.client.get('/api/v1/operations/agency-a/customers/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])
        self.assertEqual(self.client.get('/api/v1/operations/agency-b/customers/').status_code, 404)

    def test_customer_create_scoped(self):
        response = self.client.post('/api/v1/operations/agency-a/customers/', {'name': 'Client A', 'kind': 'person'}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Customer.objects.get(name='Client A').organization, self.a)

    def test_cross_tenant_order_rejected(self):
        other = Customer.objects.create(organization=self.b, name='Other')
        response = self.client.post('/api/v1/operations/agency-a/orders/', {'customer': str(other.id), 'reference': 'ORD-1'}, format='json')
        self.assertEqual(response.status_code, 404)
        self.assertFalse(ServiceOrder.objects.exists())

    def test_case_transition_is_audited(self):
        customer = Customer.objects.create(organization=self.a, name='Client')
        order = ServiceOrder.objects.create(organization=self.a, customer=customer, reference='ORD-1', created_by=self.user)
        template = WorkflowTemplate.objects.create(organization=self.a, country='Saudi Arabia', service_type='work', route='demo', approved=True)
        stage = WorkflowStage.objects.create(template=template, code='intake', label='Intake', position=1)
        case = Case.objects.create(organization=self.a, order=order, customer=customer, template=template, reference='CASE-1')
        response = self.client.post(f'/api/v1/operations/agency-a/cases/{case.id}/advance/', {}, format='json')
        self.assertEqual(response.status_code, 200)
        case.refresh_from_db()
        self.assertEqual(case.current_stage, stage)
        self.assertEqual(case.events.count(), 1)