from django.test import TestCase
from models import Filing, Db, DirectorFiling, other_directorships, Highlight
import os
from django.test import Client
from django.core.urlresolvers import reverse
import views
from django.contrib.auth.models import User
from match_directors_across_filings import get_data, all_edges, matched_ids


class MyTestCase(TestCase):

    fixtures = [os.path.join(os.path.dirname(__file__), 'fixtures.json')]

    def setUp(self):
        self._set_client()
        Db.create_all()

    def _set_client(self):
        c = Client()
        u = User.objects.get(username='fred')
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
        self.assertTrue('fred' in response.content)
        self.assertEquals(response.status_code, 200)

    def test_no_html_or_body(self):
        self._test_highlight('822663/000082266303000019')

    def test_ugly_doctype(self):
        self._test_highlight('769397/000076939713000018')

    def test_no_head(self):
        self._test_highlight('913144/000114544307001203')

    def test_director_names(self):
        folder = '822663/000082266303000019'
        f, created = Filing.objects.get_or_create(folder=folder)
        names = f.director_names()
        self.assertTrue("Benacin, Philippe" in names)

    def test_other_directorships(self):
        rows = other_directorships('4231.45610')
        self.assertEquals(rows[0][1], "HAVERTY FURNITURE COMPANIES INC")


class TestMatching(TestCase):

    fixtures = [os.path.join(os.path.dirname(__file__), 'fixtures.json')]

    def test_get_data(self):
        expected_count = DirectorFiling.objects.count()
        df = get_data()
        self.assertEquals(df.shape[0], expected_count)

    def test_matched_ids(self):
        l = matched_ids(all_edges(get_data()))
        self.assertEquals(len(list(l)), 2)
