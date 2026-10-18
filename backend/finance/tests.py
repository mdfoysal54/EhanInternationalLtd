from datetime import date
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from core.models import Organization
from .models import Account, Journal, JournalLine
from .services import post_journal

class JournalTests(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name='Finance Test Org', slug='finance-test')
        self.user = get_user_model().objects.create_user(username='fin_tester', password='test-password-123')
        self.cash = Account.objects.create(organization=self.org,code='1010',name='Cash',kind='asset')
        self.adv = Account.objects.create(organization=self.org,code='2200',name='Customer advances',kind='liability')
        self.j = Journal.objects.create(organization=self.org,reference='TEST-001',memo='Advance received',date=date.today(),created_by=self.user)

    def test_balanced_journal_posts(self):
        JournalLine.objects.create(journal=self.j,account=self.cash,debit=Decimal('100.00'))
        JournalLine.objects.create(journal=self.j,account=self.adv,credit=Decimal('100.00'))
        post_journal(journal_id=self.j.id)
        self.j.refresh_from_db()
        self.assertIsNotNone(self.j.posted_at)
        with self.assertRaises(ValidationError):
            post_journal(journal_id=self.j.id)

    def test_unbalanced_journal_rejected(self):
        JournalLine.objects.create(journal=self.j,account=self.cash,debit=Decimal('100.00'))
        JournalLine.objects.create(journal=self.j,account=self.adv,credit=Decimal('90.00'))
        with self.assertRaises(ValidationError):
            post_journal(journal_id=self.j.id)
        self.j.refresh_from_db()
        self.assertIsNone(self.j.posted_at)

    def test_cross_tenant_account_rejected(self):
        other = Organization.objects.create(name='Other Finance Org',slug='other-finance')
        wrong = Account.objects.create(organization=other,code='1010',name='Other cash',kind='asset')
        JournalLine.objects.create(journal=self.j,account=self.cash,debit=Decimal('100.00'))
        JournalLine.objects.create(journal=self.j,account=wrong,credit=Decimal('100.00'))
        with self.assertRaises(ValidationError):
            post_journal(journal_id=self.j.id)
