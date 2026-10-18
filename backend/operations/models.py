import uuid
from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from core.models import Organization, Service


def uid():
    return uuid.uuid4()


class Owned(models.Model):
    id = models.UUIDField(primary_key=True, default=uid, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Customer(Owned):
    KIND = [('person', 'Individual'), ('company', 'Company')]
    kind = models.CharField(max_length=12, choices=KIND, default='person')
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=35, blank=True)
    email = models.EmailField(blank=True)
    country = models.CharField(max_length=80, blank=True)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Supplier(Owned):
    name = models.CharField(max_length=200)
    kind = models.CharField(max_length=50, default='general')
    contact = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name


class ServiceOrder(Owned):
    STATUS = [('draft', 'Draft'), ('approved', 'Approved'), ('active', 'Active'), ('completed', 'Completed'), ('cancelled', 'Cancelled')]
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    reference = models.CharField(max_length=40)
    status = models.CharField(max_length=12, choices=STATUS, default='draft')
    description = models.TextField(blank=True)
    currency = models.CharField(max_length=3, default='BDT')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['organization', 'reference'], name='ops_order_ref_unique')]

    def clean(self):
        if self.customer_id and self.organization_id != self.customer.organization_id:
            raise ValidationError('Customer belongs to another organization')

    def __str__(self):
        return self.reference


class OrderLine(models.Model):
    order = models.ForeignKey(ServiceOrder, on_delete=models.CASCADE, related_name='lines')
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    description = models.CharField(max_length=250)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)

    def clean(self):
        if self.order_id and self.service_id and self.order.organization_id != self.service.organization_id:
            raise ValidationError('Service belongs to another organization')
        if self.quantity <= 0 or self.unit_price < 0:
            raise ValidationError('Invalid quantity or unit price')

    @property
    def total(self):
        return self.quantity * self.unit_price


class Invoice(Owned):
    STATUS = [('draft', 'Draft'), ('issued', 'Issued'), ('void', 'Void')]
    order = models.ForeignKey(ServiceOrder, on_delete=models.PROTECT)
    number = models.CharField(max_length=40)
    status = models.CharField(max_length=10, choices=STATUS, default='draft')
    issued_on = models.DateField(null=True, blank=True)
    due_on = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='BDT')

    class Meta:
        constraints = [models.UniqueConstraint(fields=['organization', 'number'], name='ops_invoice_num_unique')]

    def clean(self):
        if self.order_id and self.order.organization_id != self.organization_id:
            raise ValidationError('Order belongs to another organization')
        if self.order_id and self.currency != self.order.currency:
            raise ValidationError('Invoice currency must match order currency')
        if self.amount < 0:
            raise ValidationError('Invoice amount cannot be negative')


class Payment(Owned):
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name='payments')
    reference = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    received_on = models.DateField()
    method = models.CharField(max_length=30, choices=[('cash', 'Cash'), ('bank', 'Bank'), ('mfs', 'Mobile financial service')])
    verified = models.BooleanField(default=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['organization', 'reference'], name='ops_payment_ref_unique')]

    def clean(self):
        if self.invoice_id and self.invoice.organization_id != self.organization_id:
            raise ValidationError('Invoice belongs to another organization')
        if self.amount <= 0:
            raise ValidationError('Payment amount must be positive')


class WorkflowTemplate(Owned):
    service_type = models.CharField(max_length=50)
    country = models.CharField(max_length=100)
    route = models.CharField(max_length=100)
    version = models.PositiveIntegerField(default=1)
    source_url = models.URLField(blank=True)
    reviewed_on = models.DateField(null=True, blank=True)
    approved = models.BooleanField(default=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['organization', 'service_type', 'country', 'route', 'version'], name='ops_workflow_version_unique')]

    def __str__(self):
        return f'{self.country} / {self.route} v{self.version}'


class WorkflowStage(models.Model):
    template = models.ForeignKey(WorkflowTemplate, on_delete=models.CASCADE, related_name='stages')
    code = models.SlugField()
    label = models.CharField(max_length=120)
    position = models.PositiveIntegerField()
    instructions = models.TextField(blank=True)
    requires_approval = models.BooleanField(default=False)

    class Meta:
        ordering = ['position']
        constraints = [models.UniqueConstraint(fields=['template', 'code'], name='ops_stage_code_unique'), models.UniqueConstraint(fields=['template', 'position'], name='ops_stage_position_unique')]


class Case(Owned):
    STATUS = [('open', 'Open'), ('blocked', 'Blocked'), ('completed', 'Completed'), ('cancelled', 'Cancelled')]
    order = models.ForeignKey(ServiceOrder, on_delete=models.PROTECT)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    template = models.ForeignKey(WorkflowTemplate, on_delete=models.PROTECT)
    reference = models.CharField(max_length=40)
    status = models.CharField(max_length=12, choices=STATUS, default='open')
    current_stage = models.ForeignKey(WorkflowStage, on_delete=models.PROTECT, null=True, blank=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['organization', 'reference'], name='ops_case_ref_unique')]

    def clean(self):
        if self.order_id and self.order.organization_id != self.organization_id:
            raise ValidationError('Order belongs to another organization')
        if self.customer_id and self.customer.organization_id != self.organization_id:
            raise ValidationError('Customer belongs to another organization')
        if self.order_id and self.customer_id and self.order.customer_id != self.customer_id:
            raise ValidationError('Customer does not match order')
        if self.template_id and (self.template.organization_id != self.organization_id or not self.template.approved):
            raise ValidationError('Workflow must be approved and belong to this organization')
        if self.current_stage_id and self.template_id and self.current_stage.template_id != self.template_id:
            raise ValidationError('Stage does not belong to workflow')


class CaseEvent(models.Model):
    case = models.ForeignKey(Case, on_delete=models.PROTECT, related_name='events')
    stage = models.ForeignKey(WorkflowStage, on_delete=models.PROTECT)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    comment = models.TextField(blank=True)
    occurred_at = models.DateTimeField(auto_now_add=True)


class Task(Owned):
    case = models.ForeignKey(Case, on_delete=models.PROTECT)
    title = models.CharField(max_length=200)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    due_on = models.DateField(null=True, blank=True)
    done = models.BooleanField(default=False)

    def clean(self):
        if self.case_id and self.case.organization_id != self.organization_id:
            raise ValidationError('Case belongs to another organization')


class DocumentRegister(Owned):
    case = models.ForeignKey(Case, on_delete=models.PROTECT)
    document_type = models.CharField(max_length=100)
    reference = models.CharField(max_length=100, blank=True)
    received_on = models.DateField(null=True, blank=True)
    custody_location = models.CharField(max_length=150, blank=True)
    returned_on = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def clean(self):
        if self.case_id and self.case.organization_id != self.organization_id:
            raise ValidationError('Case belongs to another organization')


class Employer(Owned):
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    authorization_reference = models.CharField(max_length=150, blank=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class JobOrder(Owned):
    employer = models.ForeignKey(Employer, on_delete=models.PROTECT)
    title = models.CharField(max_length=200)
    vacancies = models.PositiveIntegerField()
    salary_description = models.CharField(max_length=150, blank=True)
    verified = models.BooleanField(default=False)

    def clean(self):
        if self.employer_id and self.employer.organization_id != self.organization_id:
            raise ValidationError('Employer belongs to another organization')


class Candidate(Owned):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    job_order = models.ForeignKey(JobOrder, on_delete=models.PROTECT)
    status = models.CharField(max_length=30, default='applied')

    def clean(self):
        if self.customer_id and self.customer.organization_id != self.organization_id:
            raise ValidationError('Customer belongs to another organization')
        if self.job_order_id and self.job_order.organization_id != self.organization_id:
            raise ValidationError('Job order belongs to another organization')


class TravelBooking(Owned):
    order = models.ForeignKey(ServiceOrder, on_delete=models.PROTECT)
    booking_type = models.CharField(max_length=30, choices=[('flight', 'Flight'), ('hotel', 'Hotel'), ('tour', 'Tour'), ('transport', 'Transport')])
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, null=True, blank=True)
    booking_reference = models.CharField(max_length=100, blank=True)
    departure_on = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=30, default='requested')

    def clean(self):
        if self.order_id and self.order.organization_id != self.organization_id:
            raise ValidationError('Order belongs to another organization')
        if self.supplier_id and self.supplier.organization_id != self.organization_id:
            raise ValidationError('Supplier belongs to another organization')


class PilgrimGroup(Owned):
    kind = models.CharField(max_length=10, choices=[('hajj', 'Hajj'), ('umrah', 'Umrah')])
    name = models.CharField(max_length=150)
    departure_on = models.DateField(null=True, blank=True)
    capacity = models.PositiveIntegerField(default=0)
    members = models.ManyToManyField(Customer, blank=True)


class StudentApplication(Owned):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    institution = models.CharField(max_length=200)
    destination_country = models.CharField(max_length=100)
    course = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=30, default='inquiry')

    def clean(self):
        if self.customer_id and self.customer.organization_id != self.organization_id:
            raise ValidationError('Customer belongs to another organization')