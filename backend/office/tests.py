from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from core.models import Organization, Membership
from .access import require_membership
class OfficeAccessTests(TestCase):
    def test_nonmember_rejected(self):
        user=get_user_model().objects.create_user(username='outsider',password='testpass123')
        org=Organization.objects.create(name='Office Org',slug='office-org')
        with self.assertRaises(PermissionDenied): require_membership(user,org)
    def test_member_accepted(self):
        user=get_user_model().objects.create_user(username='member',password='testpass123')
        org=Organization.objects.create(name='Office Org',slug='office-org')
        Membership.objects.create(user=user,organization=org,role='staff')
        self.assertEqual(require_membership(user,org).role,'staff')