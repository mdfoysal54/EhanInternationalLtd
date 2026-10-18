from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from core.models import Organization, Membership
from operations.models import Customer

class WorkspaceSecurityTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_user(username='ehanowner', password='safe-test-password')
        self.outsider = User.objects.create_user(username='outsider2', password='safe-test-password')
        self.org = Organization.objects.create(name='Workspace Test', slug='workspace-test')
        self.other = Organization.objects.create(name='Other Workspace', slug='other-workspace')
        Membership.objects.create(organization=self.org, user=self.owner, role='owner')
        self.customer = Customer.objects.create(organization=self.org, name='Existing Customer')

    def test_nonmember_cannot_view_dashboard(self):
        self.client.force_login(self.outsider)
        response = self.client.get(reverse('agency-workspace', args=[self.org.slug]))
        self.assertEqual(response.status_code, 404)

    def test_owner_can_create_customer(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse('erp-customer-new', args=[self.org.slug]), {
            'kind': 'person', 'name': 'New Customer', 'phone': '01700000000',
            'email': '', 'country': '', 'address': '', 'notes': ''
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Customer.objects.filter(organization=self.org, name='New Customer').exists())

    def test_cross_org_customer_edit_not_found(self):
        other_customer = Customer.objects.create(organization=self.other, name='Secret')
        self.client.force_login(self.owner)
        response = self.client.get(reverse('erp-customer-edit', args=[self.org.slug, other_customer.pk]))
        self.assertEqual(response.status_code, 404)

    def test_nonmember_cannot_read_customers(self):
        self.client.force_login(self.outsider)
        self.assertEqual(self.client.get(reverse('erp-customers', args=[self.org.slug])).status_code, 404)