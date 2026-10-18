from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from .models import Account, Journal, JournalLine
from .services import post_journal

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('code','name','kind','organization','active')
    list_filter = ('organization','kind','active')
    search_fields = ('code','name')

class LineInline(admin.TabularInline):
    model = JournalLine
    extra = 2

@admin.register(Journal)
class JournalAdmin(admin.ModelAdmin):
    list_display = ('reference','organization','date','posted_at')
    list_filter = ('organization','date')
    readonly_fields = ('posted_at','created_at')
    inlines = [LineInline]
    actions = ['post_selected']

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.posted_at:
            return ('organization','reference','memo','date','created_by','posted_at','created_at')
        return self.readonly_fields

    def has_delete_permission(self, request, obj=None):
        return bool(request.user.is_superuser and (obj is None or obj.posted_at is None))

    def has_change_permission(self, request, obj=None):
        return bool(request.user.is_superuser and (obj is None or obj.posted_at is None))

    @admin.action(description='Post selected balanced journals')
    def post_selected(self, request, queryset):
        for journal in queryset:
            try:
                post_journal(journal_id=journal.pk)
                self.message_user(request, f'Posted {journal.reference}', messages.SUCCESS)
            except ValidationError as exc:
                self.message_user(request, f'{journal.reference}: {exc}', messages.ERROR)
