from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.db import models
from core.models import Organization, Opportunity, Service
from operations.models import Case, Invoice
from .models import Article,Package,PortalAccess

# Public endpoints deliberately expose only explicitly published content.
def public_site(request,slug):
    org=get_object_or_404(Organization,slug=slug)
    now=timezone.now()
    articles=Article.objects.filter(organization=org,status='published',approved_by__isnull=False,published_at__lte=now).filter(models.Q(expires_at__isnull=True)|models.Q(expires_at__gt=now))[:30]
    packages=Package.objects.filter(organization=org,published=True,reviewed_by__isnull=False)[:30]
    opportunities=Opportunity.objects.filter(organization=org,published=True,verified_by__isnull=False).filter(models.Q(deadline__isnull=True)|models.Q(deadline__gte=now.date()))[:30]
    return render(request,'publishing/site.html',{'org':org,'articles':articles,'packages':packages,'opportunities':opportunities})

@login_required
def client_portal(request,slug):
    org=get_object_or_404(Organization,slug=slug)
    customers=PortalAccess.objects.filter(organization=org,user=request.user).values_list('customer_id',flat=True)
    cases=Case.objects.filter(organization=org,customer_id__in=customers).select_related('customer')[:100]
    invoices=Invoice.objects.filter(organization=org,order__customer_id__in=customers)[:100]
    return render(request,'publishing/portal.html',{'org':org,'cases':cases,'invoices':invoices})
