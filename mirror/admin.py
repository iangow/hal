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

    actions = ['load']

    def load(self, request, queryset):
        count = load_biographies()
        self.message_user(request, 'Added %d biographies.' % count)


admin.site.register(Highlight, HighlightAdmin)




# import requests
# import json
# from mirror.models import Highlight

# folder = '861884/000095015003000426'
# url = 'http://annotator-store.marder.io/search?uri=http://hal.marder.io/highlight/' + folder
# response = requests.get(url)

# d = json.loads(response.content)
# for row in d['rows']:
#     Highlight.get_or_create(**row)
