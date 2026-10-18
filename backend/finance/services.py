from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum, Q
from django.utils import timezone
from .models import Journal, JournalLine


@transaction.atomic
def post_journal(*, journal_id):
    journal = Journal.objects.select_for_update().get(pk=journal_id)
    if journal.posted_at:
        raise ValidationError('Journal is already posted')
    lines = list(JournalLine.objects.select_related('account').filter(journal=journal))
    if len(lines) < 2:
        raise ValidationError('A journal requires at least two lines')
    if any(line.account.organization_id != journal.organization_id for line in lines):
        raise ValidationError('Cross-organization account is not allowed')
    if any(not line.account.active for line in lines):
        raise ValidationError('Inactive accounts cannot be posted')
    if any(line.debit < 0 or line.credit < 0 or ((line.debit > 0) == (line.credit > 0)) for line in lines):
        raise ValidationError('Invalid debit/credit lines')
    debit = sum((line.debit for line in lines), Decimal('0.00'))
    credit = sum((line.credit for line in lines), Decimal('0.00'))
    if debit != credit or debit <= 0:
        raise ValidationError('Journal debits and credits must balance')
    journal.posted_at = timezone.now()
    journal.save(update_fields=['posted_at'])
    return journal


def trial_balance(organization):
    from .models import Account
    return list(Account.objects.filter(organization=organization).annotate(
        total_debit=Sum('journalline__debit', filter=Q(journalline__journal__posted_at__isnull=False)),
        total_credit=Sum('journalline__credit', filter=Q(journalline__journal__posted_at__isnull=False)),
    ).values('code','name','kind','total_debit','total_credit').order_by('code'))
