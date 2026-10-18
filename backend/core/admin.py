from django.contrib import admin
# Step 1 administrative access is superuser-only until complete tenant RBAC exists.
admin.site.has_permission = lambda request: request.user.is_active and request.user.is_superuser
from .models import Organization, Membership, Service, Opportunity, Inquiry

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display=('name','slug','created_at')
    prepopulated_fields={'slug':('name',)}

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display=('user','organization','role')
    list_filter=('organization','role')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display=('title','organization','category','published','price_from')
    list_filter=('organization','category','published')
    prepopulated_fields={'slug':('title',)}
    def get_queryset(self,request):
        qs=super().get_queryset(request)
        if request.user.is_superuser: return qs
        return qs.filter(organization__memberships__user=request.user).distinct()
    def get_readonly_fields(self,request,obj=None):
        return () if request.user.is_superuser else ('organization',)
    def save_model(self,request,obj,form,change):
        if not request.user.is_superuser and not change:
            membership=Membership.objects.filter(user=request.user,role__in=['owner','manager']).first()
            if not membership: raise PermissionError('Manager membership required')
            obj.organization=membership.organization
        super().save_model(request,obj,form,change)

@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display=('title','country','organization','published','verified_by','deadline')
    list_filter=('organization','country','published')
    def get_queryset(self,request):
        qs=super().get_queryset(request)
        return qs if request.user.is_superuser else qs.filter(organization__memberships__user=request.user).distinct()
    def save_model(self,request,obj,form,change):
        if obj.published and not obj.authorization_reference:
            from django.core.exceptions import ValidationError
            raise ValidationError('Authorization reference required for publication')
        super().save_model(request,obj,form,change)

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display=('name','phone','organization','status','created_at')
    list_filter=('organization','status')
    readonly_fields=('name','email','phone','message','consent','created_at','organization','service')
    def get_queryset(self,request):
        qs=super().get_queryset(request)
        return qs if request.user.is_superuser else qs.filter(organization__memberships__user=request.user).distinct()
