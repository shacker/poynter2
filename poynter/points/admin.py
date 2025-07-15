from django.contrib import admin
from django.db import models
from jsoneditor.forms import JSONEditor

from .forms import TicketForm
from .models import Project, Snapshot, Space, Ticket


class TicketAdmin(admin.ModelAdmin):
    form = TicketForm
    list_display = ("title", "active", "archived", "space", "created")


class SpaceAdmin(admin.ModelAdmin):
    list_display = ("project", "moderator", "is_open")
    filter_horizontal = ("members",)


class SnapshotAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.JSONField: {"widget": JSONEditor()},
    }


admin.site.register(Space, SpaceAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Project)
admin.site.register(Snapshot, SnapshotAdmin)
