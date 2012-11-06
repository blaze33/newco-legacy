import os
import types
import sys
import timeit
from django.utils import unittest
from django.test.client import RequestFactory, Client
from django.core.urlresolvers import reverse, RegexURLResolver, NoReverseMatch
from django.contrib.auth.models import AnonymousUser


class UrlTest(unittest.TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.client = Client()
        self.request = self.factory.get('/')
        self.request.user = AnonymousUser()

    def test_homepage(self):
        ''' Homepage: unit '''
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response._is_rendered, True)

    def test_homepage_bench(self):
        ''' Homepage: benchmark '''
        n = os.environ.get('BENCHMARK')
        if not n:
            print 'no benchmark ',
            sys.stdout.flush()
            return
        try:
            n = int(n)
        except Exception, err:
            print err
        t = timeit.timeit(self.test_homepage, setup=self.setUp, number=n)
        print 'Homepage rendered', n, 'times:', (t / n) * 1000, 'ms/view'

    def runTest(self):
        pass


def urltest_generator(url=None, skipped=True):
    ''' URL test generator '''
    @unittest.skipIf(skipped, 'gen skipped')
    def test_url(self=None, url=url):
        if not self:
            self = UrlTest()
            self.setUp()
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 500)
        print response.status_code, ' ',
        sys.stdout.flush()
    return test_url


"""
Test all urls not requiring arguments, ie. ignoring NoReverseMatch errors.
Only test we do not get 500 errors.

UrlTest class methods are populated with url_test_generator
"""
from ..urls import urlpatterns
n, success, skipped = 0, 0, 0
for pattern in urlpatterns:
    if isinstance(pattern, RegexURLResolver):
        if isinstance(pattern.urlconf_name, list):
            urlpatterns += [p for p in pattern.urlconf_name]
        elif isinstance(pattern.urlconf_name, types.ModuleType):
            urlpatterns += pattern.urlconf_name.urlpatterns
        continue
    if not pattern.name:
        continue
    n += 1
    try:
        url = reverse(pattern.name)
    except NoReverseMatch:
        skipped += 1
        continue
    test = urltest_generator(url, skipped=False)
    test.__doc__ = 'URL {2:3} {0} {1}'.format(pattern.name, url, n)
    test_name = 'test_{0:03}_{1}'.format(n, pattern.name)
    setattr(UrlTest, test_name, test)
    success += 1
print n, 'discovered urls,', skipped, 'skipped,', success, 'to test.'
