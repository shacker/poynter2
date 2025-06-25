from django.contrib import admin

from .forms import TicketForm
from .models import Project, Space, Ticket


class TicketAdmin(admin.ModelAdmin):
    form = TicketForm
    list_display = ("title", "active", "space", "created")


class SpaceAdmin(admin.ModelAdmin):
    list_display = ("project", "moderator", "is_open")
    filter_horizontal = ("members",)


admin.site.register(Space, SpaceAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Project)
