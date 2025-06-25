import csv

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.http import HttpResponse

User = get_user_model()


def export_to_csv(self, request, queryset):
    field_names = [
        "username",
        "first_name",
        "last_name",
        "email",
        "is_active",
        "is_staff",
        "is_superuser",
        "groups",
        "last_login",
    ]
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename={}.csv".format("User Download")
    writer = csv.writer(response)
    writer.writerow(field_names)

    for obj in queryset:
        group_set = obj.groups.all()
        groups = [getattr(group, "name") for group in group_set]
        writer.writerow(
            [groups if field == "groups" else getattr(obj, field) for field in field_names]
        )
    return response


export_to_csv.short_description = "Export to CSV"


class UserAdmin(admin.ModelAdmin):
    """
    Registers the action in User model admin
    """

    list_filter = ["is_active", "is_superuser"]
    actions = [export_to_csv]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
