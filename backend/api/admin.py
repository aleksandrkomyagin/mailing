from django.contrib import admin

from . import models


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'tag',
    )


@admin.register(models.Code)
class CodeAdmin(admin.ModelAdmin):
    list_display = (
        'code',
    )


@admin.register(models.Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = (
        'first_name', 'last_name',
        'telephone', 'email', 'code_mobile_operator',
        'tag', 'time_zone',
    )


@admin.register(models.Mail)
class MailAdmin(admin.ModelAdmin):
    list_display = (
        'create_date', 'status',
    )
    readonly_fields = ('create_date', 'client')

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(models.Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = (
        'start_time', 'tag_filter',
        'code_mobile_operator_filter',
        'end_time',
    )
