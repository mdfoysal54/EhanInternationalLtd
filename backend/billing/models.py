import uuid
from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from core.models import Organization
from operations.models import Invoice, Payment, Supplier, Customer
from finance.models import Journal

class PostingLink(models.Model):
    organization=models.ForeignKey(Organization,on_delete=models.PROTECT)
    kind=models.CharField(max_length=30)
    source_id=models.UUIDField()
    journal=models.OneToOneField(Journal,on_delete=models.PROTECT)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['organization','kind','source_id'],name='billing_post_once')]

class Allocation(models.Model):
    payment=models.ForeignKey(Payment,on_delete=models.PROTECT,related_name='allocations')
    invoice=models.ForeignKey(Invoice,on_delete=models.PROTECT,related_name='allocations')
    amount=models.DecimalField(max_digits=15,decimal_places=2)
    def clean(self):
        if self.payment_id and self.invoice_id:
            if self.payment.organization_id!=self.invoice.organization_id: raise ValidationError('Cross-organization allocation')
            if self.payment.invoice.order.currency!=self.invoice.currency: raise ValidationError('Currency mismatch')
        if self.amount<=0: raise ValidationError('Positive allocation required')

class Expense(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    organization=models.ForeignKey(Organization,on_delete=models.PROTECT)
    supplier=models.ForeignKey(Supplier,on_delete=models.PROTECT)
    description=models.CharField(max_length=250)
    amount=models.DecimalField(max_digits=15,decimal_places=2)
    incurred_on=models.DateField()
    approved_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,null=True,blank=True)
    def clean(self):
        if self.supplier_id and self.organization_id!=self.supplier.organization_id: raise ValidationError('Supplier organization mismatch')
        if self.amount<=0: raise ValidationError('Positive amount required')

class Refund(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    payment=models.ForeignKey(Payment,on_delete=models.PROTECT)
    amount=models.DecimalField(max_digits=15,decimal_places=2)
    reason=models.TextField()
    approved_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,null=True,blank=True)
    paid_at=models.DateTimeField(null=True,blank=True)
    def clean(self):
        if self.amount<=0: raise ValidationError('Positive amount required')

class TaxCode(models.Model):
    organization=models.ForeignKey(Organization,on_delete=models.PROTECT)
    code=models.CharField(max_length=30)
    rate=models.DecimalField(max_digits=7,decimal_places=4)
    active=models.BooleanField(default=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['organization','code'],name='billing_taxcode_unique')]

class BankStatementLine(models.Model):
    organization=models.ForeignKey(Organization,on_delete=models.PROTECT)
    bank_reference=models.CharField(max_length=120)
    transaction_date=models.DateField()
    amount=models.DecimalField(max_digits=15,decimal_places=2)
    matched_journal=models.ForeignKey(Journal,on_delete=models.PROTECT,null=True,blank=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['organization','bank_reference'],name='billing_bank_ref_unique')]