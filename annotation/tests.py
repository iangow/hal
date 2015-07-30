from django.test import TestCase, Client
from models import Annotation


class AnnotationTests(TestCase):

    def _check_count(self, n):
        self.assertEquals(Annotation.objects.count(), n)

    def test_search(self):
        pass

    def test_create(self):
        data = {
            "id": 1,
            "quote": "Test quote.",
            "ranges": "[{u'start': u'/p', u'end': u'/p', u'startOffset': 1, u'endOffset': 10}]",
            "text": "",
            "uri": "/highlight/101271/000110465907029331"
        }
        path = '/annotations'
        response = Client().post(path, data)
        self._check_count(1)
        a = Annotation.objects.all()[0]
        self.assertEquals(a.quote, data['quote'])

    def test_read(self):
        pass

    def test_update(self):
        pass

    def test_delete(self):
        self._check_count(0)
        self.test_create()
        self._check_count(1)
        Client().delete('/annotations/1')
        self._check_count(0)
