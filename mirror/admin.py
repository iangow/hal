from django.contrib import admin
from .models import Filing, Highlight


class FilingAdmin(admin.ModelAdmin):

    actions = ['sync']

    def sync(self, request, queryset):
        count = Filing.sync()
        self.message_user(request, 'Added %d filings.' % count)


admin.site.register(Filing, FilingAdmin)


def load_biographies():
    count = 0
    for d in bios():
        d['filing'] = Filing.objects.get(folder=d['filing'])
        try:
            b = Biography.objects.get(
                filing=d['filing'], director_name=d['director_name']
            )
        except Biography.DoesNotExist:
            d['text'] = clean(d['text'])
            b = Biography.objects.create(**d)
            count += 1
    return count


class HighlightAdmin(admin.ModelAdmin):

    actions = ['load']

    def load(self, request, queryset):
        count = load_biographies()
        self.message_user(request, 'Added %d biographies.' % count)


admin.site.register(Highlight, HighlightAdmin)
