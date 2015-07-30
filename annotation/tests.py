from django.test import TestCase, Client
from models import Annotation
import json


class AnnotationTests(TestCase):

    def setUp(self):
        self.data = {
            "id": 1,
            "quote": "Test quote.",
            "ranges": "[{u'start': u'/p', u'end': u'/p', u'startOffset': 1, u'endOffset': 10}]",
            "text": "",
            "uri": "/highlight/101271/000110465907029331"
        }
        self._check_count(0)
        self._create_annotation(self.data)
        self._check_count(1)

    def _check_count(self, n):
        self.assertEquals(Annotation.objects.count(), n)

    def _create_annotation(self, data):
        path = '/annotations'
        Client().post(path, data)

    def _search(self, path):
        response = Client().get(path)
        return json.loads(response.content)

    def test_search(self):
        new_data = {
            "quote": ".",
            "ranges": ".",
            "text": ".",
            "uri": "/new/page"
        }
        self._create_annotation(new_data)
        path = '/search?format=json&uri=%2Fhighlight%2F101271%2F000110465907029331'
        data = self._search(path)
        self.assertEquals(len(data), 1)
        path = '/search?format=json'
        data = self._search(path)
        self.assertEquals(len(data), 2)

    def test_create(self):
        a = Annotation.objects.all()[0]
        self.assertEquals(a.quote, self.data['quote'])

    def test_read(self):
        response = Client().get('/annotations/1')
        response_data = json.loads(response.content)
        self.assertEquals(response_data['quote'], self.data['quote'])

    def test_update(self):
        new_quote = 'Hello World!'
        data = self.data.copy()
        data['quote'] = new_quote
        response = Client().put('/annotations/1', json.dumps(data), content_type='application/json')
        self._check_count(1)
        a = Annotation.objects.all()[0]
        self.assertEquals(a.quote, new_quote)

    def test_delete(self):
        Client().delete('/annotations/1')
        self._check_count(0)
