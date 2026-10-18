from django.contrib import admin
from . import models

# Step 2 retains the Step 1 superuser-only Django admin boundary.
# Non-superuser agency staff use the tenant-scoped API after permission review.

class OwnedAdmin(admin.ModelAdmin):
    list_display = ('id', 'organization', 'created_at')
    list_filter = ('organization',)
    readonly_fields = ('created_at',)

    def save_model(self, request, obj, form, change):
        obj.full_clean()
        super().save_model(request, obj, form, change)


for model in [models.Customer, models.Supplier, models.ServiceOrder, models.Invoice,
              models.Payment, models.WorkflowTemplate, models.Case, models.Task,
              models.DocumentRegister, models.Employer, models.JobOrder,
              models.Candidate, models.TravelBooking, models.PilgrimGroup,
              models.StudentApplication]:
    admin.site.register(model, OwnedAdmin)

@admin.register(models.OrderLine)
class OrderLineAdmin(admin.ModelAdmin):
    list_display = ('order', 'service', 'quantity', 'unit_price')
    def save_model(self, request, obj, form, change):
        obj.full_clean()
        super().save_model(request, obj, form, change)

@admin.register(models.WorkflowStage)
class WorkflowStageAdmin(admin.ModelAdmin):
    list_display = ('template', 'position', 'code', 'label')

@admin.register(models.CaseEvent)
class CaseEventAdmin(admin.ModelAdmin):
    list_display = ('case', 'stage', 'actor', 'occurred_at')
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False