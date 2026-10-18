import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from core.models import Organization
from operations.models import Case, Customer, DocumentRegister

class Branch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    code = models.SlugField()
    name = models.CharField(max_length=160)
    address = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['organization','code'], name='office_branch_code_unique')]
    def __str__(self): return self.name

class Department(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['branch','name'], name='office_department_unique')]
    def __str__(self): return self.name

class StaffAssignment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.SET_NULL)
    can_manage = models.BooleanField(default=False)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user','branch'], name='office_staff_branch_unique')]
    def clean(self):
        if self.department_id and self.department.branch_id != self.branch_id:
            raise ValidationError('Department must belong to branch')

class CaseAssignment(models.Model):
    case = models.OneToOneField(Case, on_delete=models.PROTECT, related_name='office_assignment')
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT)
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.PROTECT)
    def clean(self):
        if self.case_id and self.branch_id and self.case.organization_id != self.branch.organization_id:
            raise ValidationError('Cross-organization assignment forbidden')
        if self.department_id and self.department.branch_id != self.branch_id:
            raise ValidationError('Department must belong to branch')

class CustodyTransfer(models.Model):
    document = models.ForeignKey(DocumentRegister, on_delete=models.PROTECT, related_name='transfers')
    from_location = models.CharField(max_length=150)
    to_location = models.CharField(max_length=150)
    handed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='+')
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='+')
    acknowledged_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)

class PrivateUpload(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case = models.ForeignKey(Case, on_delete=models.PROTECT)
    file = models.FileField(upload_to='restricted/cases/%Y/%m/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    original_name = models.CharField(max_length=200)
    size = models.PositiveBigIntegerField()