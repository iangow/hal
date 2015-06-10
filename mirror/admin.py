from django.contrib import admin
from .models import Directors, Filing
import json


class FilingAdmin(admin.ModelAdmin):

    actions = ['sync']

    def sync(self, request, queryset):
        count = Filing.sync()
        self.message_user(request, 'Added %d filings.' % count)


admin.site.register(Directors)
admin.site.register(Filing, FilingAdmin)
