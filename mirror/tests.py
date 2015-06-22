from django.test import TestCase
from models import Filing
import os
from django.test import Client
from django.core.urlresolvers import reverse
import views
from django.contrib.auth.models import User


class MyTestCase(TestCase):

    def setUp(self):
        c = Client()
        u = User.objects.create(username='fred')
        u.set_password('secret')
        u.save()
        self.assertEquals(User.objects.count(), 1)
        self.assertTrue(
            c.login(username='fred', password='secret')
        )
        self.client = c

    def _test_highlight(self, folder):
        url = reverse(views.highlight, args=[folder])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_no_html_or_body(self):
        self._test_highlight('822663/000082266303000019')

    def test_ugly_doctype(self):
        self._test_highlight('769397/000076939713000018')

    def test_no_head(self):
        self._test_highlight('913144/000114544307001203')
