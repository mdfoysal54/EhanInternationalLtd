import uuid
from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from core.models import Organization


def new_id():
    return uuid.uuid4()


class Account(models.Model):
    TYPES = [('asset','Asset'), ('liability','Liability'), ('equity','Equity'), ('income','Income'), ('expense','Expense')]
    id = models.UUIDField(primary_key=True, default=new_id, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=120)
    kind = models.CharField(max_length=12, choices=TYPES)
    active = models.BooleanField(default=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['organization','code'],name='fin_org_account_code')]

    def __str__(self):
        return f'{self.code} - {self.name}'


class Journal(models.Model):
    id = models.UUIDField(primary_key=True, default=new_id, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    reference = models.CharField(max_length=60)
    memo = models.CharField(max_length=250)
    date = models.DateField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    posted_at = models.DateTimeField(null=True, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['organization','reference'],name='fin_org_journal_ref')]

    def __str__(self):
        return self.reference


class JournalLine(models.Model):
    journal = models.ForeignKey(Journal, related_name='lines', on_delete=models.PROTECT)
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    debit = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'))
    credit = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'))
    description = models.CharField(max_length=250, blank=True)

    def clean(self):
        if self.journal_id and self.account_id and self.journal.organization_id != self.account.organization_id:
            raise ValidationError('Account and journal must belong to the same organization')
        if self.debit < 0 or self.credit < 0 or ((self.debit > 0) == (self.credit > 0)):
            raise ValidationError('Exactly one of debit or credit must be positive')
        if self.journal_id and self.journal.posted_at is not None:
            raise ValidationError('Posted journals cannot be edited')
