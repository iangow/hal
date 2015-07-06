import requests
import json
from mirror.models import Highlight

folder = '861884/000095015003000426'
url = 'http://annotator-store.marder.io/search?uri=http://hal.marder.io/highlight/' + folder
response = requests.get(url)

d = json.loads(response.content)
for row in d['rows']:
    Highlight.get_or_create(**row)
