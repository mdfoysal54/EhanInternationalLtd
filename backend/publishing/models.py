from django.conf import settings
from django.db import models
from core.models import Organization, Service, Opportunity
from operations.models import Customer

class Article(models.Model):
    organization=models.ForeignKey(Organization,on_delete=models.PROTECT)
    slug=models.SlugField()
    title=models.CharField(max_length=180)
    body=models.TextField()
    status=models.CharField(max_length=15,choices=[('draft','Draft'),('review','Review'),('published','Published')],default='draft')
    published_at=models.DateTimeField(null=True,blank=True)
    expires_at=models.DateTimeField(null=True,blank=True)
    approved_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,null=True,blank=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['organization','slug'],name='publishing_article_slug_unique')]

class Package(models.Model):
    organization=models.ForeignKey(Organization,on_delete=models.PROTECT)
    slug=models.SlugField()
    name=models.CharField(max_length=180)
    kind=models.CharField(max_length=20,choices=[('tour','Tour'),('umrah','Umrah'),('hajj','Hajj'),('travel','Travel')])
    description=models.TextField()
    price_from=models.DecimalField(max_digits=15,decimal_places=2,null=True,blank=True)
    currency=models.CharField(max_length=3,default='BDT')
    published=models.BooleanField(default=False)
    reviewed_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,null=True,blank=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['organization','slug'],name='publishing_package_slug_unique')]

class PortalAccess(models.Model):
    organization=models.ForeignKey(Organization,on_delete=models.PROTECT)
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    customer=models.ForeignKey(Customer,on_delete=models.PROTECT)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['organization','user','customer'],name='publishing_portal_link_unique')]

class NotificationOutbox(models.Model):
    organization=models.ForeignKey(Organization,on_delete=models.PROTECT)
    recipient=models.CharField(max_length=250)
    channel=models.CharField(max_length=15,choices=[('email','Email'),('sms','SMS')])
    subject=models.CharField(max_length=200,blank=True)
    body=models.TextField()
    state=models.CharField(max_length=15,choices=[('pending','Pending'),('sent','Sent'),('failed','Failed')],default='pending')
    attempts=models.PositiveIntegerField(default=0)
    created_at=models.DateTimeField(auto_now_add=True)