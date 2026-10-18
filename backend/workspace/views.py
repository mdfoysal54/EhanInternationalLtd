from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from core.models import Membership, Inquiry
from operations.models import Customer, Case, ServiceOrder, Invoice, Task
from office.access import visible_cases
from .forms import CustomerForm


def context_for(request, slug):
    member = Membership.objects.select_related('organization').filter(
        user=request.user, organization__slug=slug
    ).first()
    if member is None:
        raise Http404('Workspace not found')
    return member.organization, member


def manager_only(member):
    if member.role not in ('owner', 'manager'):
        raise PermissionDenied('Management permission required')


def customers_for(request, org, member):
    qs = Customer.objects.filter(organization=org)
    if member.role not in ('owner', 'manager'):
        qs = qs.filter(id__in=visible_cases(request.user, org).values('customer_id'))
    return qs


@login_required
@require_GET
def dashboard(request, slug):
    org, member = context_for(request, slug)
    cases = visible_cases(request.user, org)
    customers = customers_for(request, org, member)
    manager = member.role in ('owner', 'manager')
    data = {
        'org': org, 'member': member, 'active': 'dashboard',
        'case_count': cases.filter(status='open').count(),
        'blocked_count': cases.filter(status='blocked').count(),
        'customer_count': customers.count(),
        'task_count': Task.objects.filter(organization=org, assigned_to=request.user, done=False).count(),
        'recent_cases': cases.select_related('customer').order_by('-created_at')[:8],
        'tasks': Task.objects.filter(organization=org, assigned_to=request.user, done=False).select_related('case').order_by('due_on')[:8],
        'inquiries': Inquiry.objects.filter(organization=org).order_by('-created_at')[:8] if manager else [],
    }
    return render(request, 'workspace/dashboard.html', data)


@login_required
@require_GET
def customer_list(request, slug):
    org, member = context_for(request, slug)
    qs = customers_for(request, org, member)
    term = request.GET.get('q', '').strip()[:100]
    if term:
        qs = qs.filter(Q(name__icontains=term) | Q(phone__icontains=term) | Q(email__icontains=term))
    return render(request, 'workspace/customers.html', {
        'org': org, 'member': member, 'active': 'customers', 'records': qs.order_by('name')[:100],
        'term': term, 'can_edit': member.role in ('owner', 'manager'),
    })


@login_required
@require_http_methods(['GET', 'POST'])
def customer_create(request, slug):
    org, member = context_for(request, slug)
    manager_only(member)
    form = CustomerForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.organization = org
        obj.full_clean()
        obj.save()
        return redirect('erp-customers', slug=slug)
    return render(request, 'workspace/customer_form.html', {
        'org': org, 'member': member, 'active': 'customers', 'form': form, 'heading': 'New customer'
    })


@login_required
@require_http_methods(['GET', 'POST'])
def customer_edit(request, slug, pk):
    org, member = context_for(request, slug)
    manager_only(member)
    customer = get_object_or_404(Customer, pk=pk, organization=org)
    form = CustomerForm(request.POST or None, instance=customer)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('erp-customers', slug=slug)
    return render(request, 'workspace/customer_form.html', {
        'org': org, 'member': member, 'active': 'customers', 'form': form, 'heading': 'Edit customer'
    })


@login_required
@require_GET
def case_list(request, slug):
    org, member = context_for(request, slug)
    qs = visible_cases(request.user, org).select_related('customer')
    term = request.GET.get('q', '').strip()[:100]
    if term:
        qs = qs.filter(Q(reference__icontains=term) | Q(customer__name__icontains=term))
    return render(request, 'workspace/cases.html', {
        'org': org, 'member': member, 'active': 'cases', 'records': qs.order_by('-created_at')[:100], 'term': term
    })


@login_required
@require_GET
def task_list(request, slug):
    org, member = context_for(request, slug)
    qs = Task.objects.filter(organization=org, assigned_to=request.user).select_related('case').order_by('done', 'due_on')[:100]
    return render(request, 'workspace/tasks.html', {'org': org, 'member': member, 'active': 'tasks', 'records': qs})


@login_required
@require_POST
def task_complete(request, slug, pk):
    org, member = context_for(request, slug)
    task = get_object_or_404(Task, pk=pk, organization=org, assigned_to=request.user)
    Task.objects.filter(pk=task.pk, organization=org, assigned_to=request.user, done=False).update(done=True)
    return redirect('erp-tasks', slug=slug)