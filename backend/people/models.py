import uuid
from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from core.models import Organization
from office.models import Branch

class Employee(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    organization=models.ForeignKey(Organization,on_delete=models.PROTECT)
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,null=True,blank=True)
    branch=models.ForeignKey(Branch,on_delete=models.PROTECT)
    code=models.CharField(max_length=40)
    name=models.CharField(max_length=150)
    base_salary=models.DecimalField(max_digits=14,decimal_places=2,default=Decimal('0'))
    active=models.BooleanField(default=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['organization','code'],name='people_employee_code_unique')]
    def clean(self):
        if self.branch_id and self.branch.organization_id!=self.organization_id: raise ValidationError('Branch organization mismatch')

class Shift(models.Model):
    organization=models.ForeignKey(Organization,on_delete=models.PROTECT)
    name=models.CharField(max_length=100)
    starts=models.TimeField()
    ends=models.TimeField()
    grace_minutes=models.PositiveIntegerField(default=0)

class ShiftAssignment(models.Model):
    employee=models.ForeignKey(Employee,on_delete=models.PROTECT)
    shift=models.ForeignKey(Shift,on_delete=models.PROTECT)
    starts_on=models.DateField()
    ends_on=models.DateField(null=True,blank=True)

class LeaveRequest(models.Model):
    employee=models.ForeignKey(Employee,on_delete=models.PROTECT)
    starts_on=models.DateField()
    ends_on=models.DateField()
    reason=models.TextField()
    status=models.CharField(max_length=15,choices=[('pending','Pending'),('approved','Approved'),('rejected','Rejected')],default='pending')
    reviewed_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,null=True,blank=True)
    def clean(self):
        if self.ends_on<self.starts_on: raise ValidationError('Invalid leave dates')

class AttendanceDevice(models.Model):
    organization=models.ForeignKey(Organization,on_delete=models.PROTECT)
    branch=models.ForeignKey(Branch,on_delete=models.PROTECT)
    code=models.CharField(max_length=50)
    adapter=models.CharField(max_length=50,default='csv')
    active=models.BooleanField(default=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['organization','code'],name='people_device_code_unique')]

class AttendanceEvent(models.Model):
    device=models.ForeignKey(AttendanceDevice,on_delete=models.PROTECT)
    employee=models.ForeignKey(Employee,on_delete=models.PROTECT)
    external_id=models.CharField(max_length=120)
    occurred_at=models.DateTimeField()
    received_at=models.DateTimeField(auto_now_add=True)
    kind=models.CharField(max_length=12,choices=[('in','Check in'),('out','Check out')])
    class Meta:
        constraints=[models.UniqueConstraint(fields=['device','external_id'],name='people_attendance_event_unique')]

class PayrollRun(models.Model):
    organization=models.ForeignKey(Organization,on_delete=models.PROTECT)
    month=models.DateField()
    status=models.CharField(max_length=20,choices=[('draft','Draft'),('review','Review'),('approved','Approved')],default='draft')
    approved_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,null=True,blank=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['organization','month'],name='people_payroll_month_unique')]

class Payslip(models.Model):
    run=models.ForeignKey(PayrollRun,on_delete=models.PROTECT)
    employee=models.ForeignKey(Employee,on_delete=models.PROTECT)
    base=models.DecimalField(max_digits=14,decimal_places=2)
    additions=models.DecimalField(max_digits=14,decimal_places=2,default=0)
    deductions=models.DecimalField(max_digits=14,decimal_places=2,default=0)
    @property
    def net(self): return self.base+self.additions-self.deductions
    class Meta:
        constraints=[models.UniqueConstraint(fields=['run','employee'],name='people_payslip_unique')]