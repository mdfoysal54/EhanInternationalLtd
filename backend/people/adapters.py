from dataclasses import dataclass
from datetime import datetime
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import AttendanceEvent, Employee, AttendanceDevice

@dataclass(frozen=True)
class NormalizedAttendance:
    external_id: str
    employee_code: str
    occurred_at: datetime
    kind: str

@transaction.atomic
def import_events(*, device, records):
    count=0
    for item in records:
        if item.kind not in ('in','out') or not item.external_id or item.occurred_at.tzinfo is None:
            raise ValidationError('Invalid event')
        employee=Employee.objects.get(organization=device.organization,code=item.employee_code,active=True)
        if employee.branch_id!=device.branch_id: raise ValidationError('Wrong branch')
        _,created=AttendanceEvent.objects.get_or_create(device=device,external_id=item.external_id,defaults={'employee':employee,'occurred_at':item.occurred_at,'kind':item.kind})
        count+=int(created)
    return count