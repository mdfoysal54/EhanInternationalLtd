from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_http_methods
from core.models import Organization
from operations.models import Customer, Case, Task
from .access import require_membership, visible_cases, require_case
from .models import Branch, CustodyTransfer, PrivateUpload
from django.http import FileResponse, Http404
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from django.utils.text import get_valid_filename
from pathlib import Path

@login_required
@require_http_methods(['GET','POST'])
def customers(request, slug):
    org = get_object_or_404(Organization, slug=slug)
    member = require_membership(request.user, org)
    if request.method == 'POST':
        if member.role not in ('owner','manager'):
            raise PermissionDenied('Customer creation requires manager')
        name = request.POST.get('name','').strip()
        if not name or len(name)>200: raise ValidationError('Valid name required')
        Customer.objects.create(organization=org, name=name, phone=request.POST.get('phone','')[:35])
        return redirect('office-customers',slug=slug)
    records = Customer.objects.filter(organization=org).order_by('name')[:200] if member.role in ('owner','manager') else Customer.objects.filter(id__in=visible_cases(request.user,org).values('customer_id')).order_by('name')[:200]
    return render(request,'office/customers.html',{'org':org,'records':records,'can_add':member.role in ('owner','manager')})

@login_required
@require_http_methods(['GET'])
def cases(request, slug):
    org=get_object_or_404(Organization,slug=slug)
    return render(request,'office/cases.html',{'org':org,'records':visible_cases(request.user,org).select_related('customer').order_by('-created_at')[:200]})

@login_required
@require_http_methods(['GET'])
def case_detail(request, slug, pk):
    org=get_object_or_404(Organization,slug=slug)
    case=get_object_or_404(Case,pk=pk,organization=org)
    require_case(request.user,case)
    return render(request,'office/case.html',{'org':org,'case':case,'events':case.events.select_related('actor','stage').order_by('-occurred_at')[:100],'docs':PrivateUpload.objects.filter(case=case).order_by('-created_at')})

@login_required
@require_http_methods(['POST'])
def upload(request, slug, pk):
    org=get_object_or_404(Organization,slug=slug)
    case=get_object_or_404(Case,pk=pk,organization=org)
    require_case(request.user,case)
    f=request.FILES.get('file')
    if not f or f.size>5*1024*1024: raise ValidationError('File missing or exceeds 5 MB')
    from django.core.files.uploadedfile import UploadedFile
    header=f.read(8); f.seek(0)
    if not (header.startswith(b'%PDF-') or header.startswith(b'\x89PNG\r\n\x1a\n') or header.startswith(b'\xff\xd8\xff')):
        raise ValidationError('Only PDF, PNG and JPEG files are accepted')
    PrivateUpload.objects.create(case=case,file=f,uploaded_by=request.user,original_name=get_valid_filename(Path(f.name).name)[:200],size=f.size)
    return redirect('office-case',slug=slug,pk=case.pk)

@login_required
@require_http_methods(['GET'])
def download(request, slug, pk):
    doc=get_object_or_404(PrivateUpload,pk=pk,case__organization__slug=slug)
    require_case(request.user,doc.case)
    if not default_storage.exists(doc.file.name): raise Http404()
    response=FileResponse(doc.file.open('rb'),as_attachment=True,filename=doc.original_name)
    response['Cache-Control']='private, no-store'
    response['X-Content-Type-Options']='nosniff'
    return response