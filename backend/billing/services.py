from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from finance.models import Account, Journal, JournalLine
from finance.services import post_journal
from operations.models import Invoice, Payment
from .models import PostingLink, Allocation

@transaction.atomic
def allocate_payment(*, payment_id, invoice_id, amount):
    payment=Payment.objects.select_for_update().get(pk=payment_id)
    invoice=Invoice.objects.select_for_update().get(pk=invoice_id)
    amount=Decimal(str(amount))
    if not payment.verified: raise ValidationError('Unverified payment')
    if invoice.status!='issued': raise ValidationError('Invoice not issued')
    if payment.organization_id!=invoice.organization_id or payment.invoice.currency!=invoice.currency:
        raise ValidationError('Organization or currency mismatch')
    if amount<=0: raise ValidationError('Amount must be positive')
    used=Allocation.objects.filter(payment=payment).aggregate(s=Sum('amount'))['s'] or Decimal('0')
    invoice_used=Allocation.objects.filter(invoice=invoice).aggregate(s=Sum('amount'))['s'] or Decimal('0')
    if used+amount>payment.amount or invoice_used+amount>invoice.amount:
        raise ValidationError('Allocation exceeds payment or invoice balance')
    return Allocation.objects.create(payment=payment,invoice=invoice,amount=amount)

@transaction.atomic
def post_verified_receipt(*, payment_id, cash_account_id, advance_account_id, actor):
    payment=Payment.objects.select_for_update().select_related('invoice').get(pk=payment_id)
    if not payment.verified: raise ValidationError('Payment must be verified')
    if PostingLink.objects.filter(organization=payment.organization,kind='receipt',source_id=payment.pk).exists():
        raise ValidationError('Receipt already posted')
    cash=Account.objects.get(pk=cash_account_id,organization=payment.organization,active=True)
    advance=Account.objects.get(pk=advance_account_id,organization=payment.organization,active=True)
    if cash.kind!='asset' or advance.kind!='liability': raise ValidationError('Expected asset and liability accounts')
    journal=Journal.objects.create(organization=payment.organization,reference=f'RCPT-{payment.pk.hex[:24]}',memo=f'Receipt {payment.reference}',date=payment.received_on,created_by=actor)
    JournalLine.objects.create(journal=journal,account=cash,debit=payment.amount,credit=0)
    JournalLine.objects.create(journal=journal,account=advance,debit=0,credit=payment.amount)
    post_journal(journal_id=journal.pk)
    PostingLink.objects.create(organization=payment.organization,kind='receipt',source_id=payment.pk,journal=journal)
    return journal