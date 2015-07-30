from django.contrib import admin
from .models import Filing


class FilingAdmin(admin.ModelAdmin):

    list_display = ('folder', 'type', 'text_file')
    list_filter = ('type', 'text_file')


admin.site.register(Filing, FilingAdmin)
