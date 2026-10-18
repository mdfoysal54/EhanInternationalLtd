from django.contrib import admin
from .models import Article,Package,PortalAccess,NotificationOutbox
for model in (Article,Package,PortalAccess,NotificationOutbox): admin.site.register(model)