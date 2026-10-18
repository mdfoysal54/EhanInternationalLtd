from django.contrib import admin
from .models import Branch, Department, StaffAssignment, CaseAssignment, CustodyTransfer, PrivateUpload
for model in (Branch,Department,StaffAssignment,CaseAssignment,CustodyTransfer,PrivateUpload):
    admin.site.register(model)