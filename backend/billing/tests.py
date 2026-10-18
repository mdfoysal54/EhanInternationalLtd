from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import Organization
from finance.models import Account
class BillingTests(TestCase):
    def test_accounts_are_tenant_scoped(self):
        org=Organization.objects.create(name='A',slug='a')
        Account.objects.create(organization=org,code='1010',name='Cash',kind='asset')
        self.assertEqual(Account.objects.filter(organization=org).count(),1)