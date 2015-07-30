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
        self._create_annotation()
        self._check_count(1)

    def _check_count(self, n):
        self.assertEquals(Annotation.objects.count(), n)

    def _create_annotation(self):
        path = '/annotations'
        Client().post(path, self.data)

    def test_search(self):
        pass

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
