from django.contrib import admin
from .models import Filing, Highlight


class FilingAdmin(admin.ModelAdmin):

    list_display = ('folder', 'type', 'text_file')
    list_filter = ('type', 'text_file')


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

    list_display = ('id', 'uri', 'highlighted_by', 'text')
    list_filter = ('highlighted_by', )


admin.site.register(Highlight, HighlightAdmin)
