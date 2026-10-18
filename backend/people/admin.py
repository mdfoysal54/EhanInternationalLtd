from django.contrib import admin
from .models import Employee,Shift,ShiftAssignment,LeaveRequest,AttendanceDevice,AttendanceEvent,PayrollRun,Payslip
for model in (Employee,Shift,ShiftAssignment,LeaveRequest,AttendanceDevice,AttendanceEvent,PayrollRun,Payslip): admin.site.register(model)
