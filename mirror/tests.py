from django.test import TestCase
from models import Filing
import os
from django.test import Client
from django.core.urlresolvers import reverse
import views


class MyTestCase(TestCase):

    FOLDERS = [
        '769397/000076939713000018',
        # '913144/000114544307001203'
    ]

    def test_mirror(self):
        c = Client()
        for folder in self.FOLDERS:
            url = reverse(views.highlight, args=[folder])
            response = c.get(url)
            self.assertEquals(response.status_code, 200)
