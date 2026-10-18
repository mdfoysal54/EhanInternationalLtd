import uuid
from django.db import models
from django.conf import settings

def uid(): return uuid.uuid4()

class Organization(models.Model):
    id=models.UUIDField(primary_key=True,default=uid,editable=False)
    name=models.CharField(max_length=200,unique=True)
    slug=models.SlugField(unique=True)
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name

class Membership(models.Model):
    ROLE_CHOICES=[('owner','Owner'),('manager','Manager'),('staff','Staff')]
    organization=models.ForeignKey(Organization,on_delete=models.CASCADE,related_name='memberships')
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='agency_memberships')
    role=models.CharField(max_length=20,choices=ROLE_CHOICES,default='staff')
    class Meta:
        constraints=[models.UniqueConstraint(fields=['organization','user'],name='unique_org_member')]

class Service(models.Model):
    organization=models.ForeignKey(Organization,on_delete=models.CASCADE,related_name='services')
    title=models.CharField(max_length=180)
    slug=models.SlugField()
    category=models.CharField(max_length=80,choices=[(v,v) for v in ['Manpower','Work Visa','Tourism','Travel','Hajj','Umrah','Student','Other']])
    description=models.TextField(blank=True)
    price_from=models.DecimalField(max_digits=13,decimal_places=2,null=True,blank=True)
    currency=models.CharField(max_length=3,default='BDT')
    published=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['organization','slug'],name='unique_org_service_slug')]
    def __str__(self): return self.title

class Opportunity(models.Model):
    organization=models.ForeignKey(Organization,on_delete=models.CASCADE,related_name='opportunities')
    title=models.CharField(max_length=180)
    country=models.CharField(max_length=100)
    description=models.TextField(blank=True)
    employer=models.CharField(max_length=180,blank=True)
    vacancies=models.PositiveIntegerField(default=0)
    deadline=models.DateField(null=True,blank=True)
    authorization_reference=models.CharField(max_length=180,blank=True)
    verified_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True)
    published=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.title

class Inquiry(models.Model):
    organization=models.ForeignKey(Organization,on_delete=models.CASCADE,related_name='inquiries')
    service=models.ForeignKey(Service,on_delete=models.SET_NULL,null=True,blank=True)
    name=models.CharField(max_length=150)
    email=models.EmailField(blank=True)
    phone=models.CharField(max_length=35)
    message=models.TextField(max_length=3000)
    consent=models.BooleanField(default=False)
    status=models.CharField(max_length=20,choices=[('new','New'),('contacted','Contacted'),('closed','Closed')],default='new')
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self): return f'{self.name} - {self.organization.name}'
