from django.core.exceptions import PermissionDenied
from core.models import Membership
from .models import StaffAssignment, CaseAssignment

def require_membership(user, org):
    if not user.is_authenticated:
        raise PermissionDenied('Authentication required')
    membership = Membership.objects.filter(user=user, organization=org).first()
    if membership is None:
        raise PermissionDenied('No organization membership')
    return membership

def visible_cases(user, org):
    from operations.models import Case
    membership = require_membership(user, org)
    base = Case.objects.filter(organization=org)
    if membership.role in ('owner','manager'):
        return base
    branches = StaffAssignment.objects.filter(user=user, branch__organization=org).values_list('branch_id', flat=True)
    return base.filter(office_assignment__branch_id__in=branches)

def require_case(user, case):
    if not visible_cases(user, case.organization).filter(pk=case.pk).exists():
        raise PermissionDenied('Case access denied')