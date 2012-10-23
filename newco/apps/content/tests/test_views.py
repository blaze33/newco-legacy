import os
import timeit
from django.conf import settings
from django.utils import unittest
from django.test.client import RequestFactory, Client
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, AnonymousUser
from ..views import ContentCreateView, ContentDeleteView, ContentDetailView


class SimpleTest(unittest.TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.client = Client()
        self.request = self.factory.get('/')
        self.request.user = AnonymousUser()
        self.views = [ContentCreateView, ContentDeleteView, ContentDetailView]

    def test_redirect_anon(self):
        '''
        Content: AnonymousUser is redirected
        '''
        for view in self.views:
            response = view().dispatch(self.request)
            self.assertEqual(response.status_code, 302)
            assert settings.LOGIN_URL in response._headers['location'][1]

    def test_non_staff_fordidden(self):
        '''
        Content: non staff user is fordidden
        '''
        request = self.request
        request.user = User()
        for view in self.views:
            self.assertRaises(PermissionDenied, view().dispatch, request)

    def test_homepage(self):
        ''' Homepage: unit '''
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response._is_rendered, True)

    def test_homepage_bench(self):
        ''' Homepage: benchmark '''
        n = os.environ.get('BENCHMARK')
        if not n:
            print 'no benchmark'
            return
        try:
            n = int(n)
        except Exception, err:
            print err
        t = timeit.timeit(self.test_homepage, setup=self.setUp, number=n)
        print 'Homepage rendered', n, 'times:', (t / n) * 1000, 'ms/view'
