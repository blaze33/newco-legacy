import os
import types
import sys
import timeit
from django.utils import unittest
from django.test.client import RequestFactory, Client
from django.core.urlresolvers import reverse, RegexURLResolver, NoReverseMatch
from django.contrib.auth.models import AnonymousUser
from fnmatch import fnmatch


def pycall_django_filter(call_stack, module_name, class_name, func_name, full_name):
    exclude = ['pycallgraph.*', 'django.*']
    include = ['compressor.base*', 'storages.*', 'boto.*']
    for pattern in include:
        if fnmatch(full_name, pattern):
            return True
    for pattern in exclude:
        if fnmatch(full_name, pattern):
            return False
    return False


def print_progress(step=0, number=1, padding=''):
    sys.stdout.write('\r{0}{1:>4.0%} {2}/{3}'.format(padding, float(step) / number, step, number))
    sys.stdout.flush()


class UrlTest(unittest.TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.client = Client()
        self.request = self.factory.get('/')
        self.request.user = AnonymousUser()

    def test_homepage(self):
        ''' Homepage: unit '''
        url = os.environ.get('URL', reverse('home'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response._is_rendered, True)
        if hasattr(self, 'n'):
            self.i += 1
            print_progress(self.i, self.n, "Homepage: benchmark ... ")

    def test_homepage_bench(self):
        ''' Homepage: benchmark '''
        n = os.environ.get('BENCHMARK')
        graph = os.environ.get('GRAPH')
        if not n:
            print 'no benchmark ',
            sys.stdout.flush()
            return
        try:
            self.n = int(n)
            self.i = 0
        except Exception, err:
            print err
        try:
            from compressor.storage import default_storage
            default_storage.entries
        except:
            pass
        if graph:
            try:
                import pycallgraph
                pycallgraph.start_trace(filter_func=pycall_django_filter)
            except:
                print "install pycallgraph to draw profiling graph"
                graph = None
        t = timeit.timeit(self.test_homepage, setup=self.setUp, number=self.n)
        if graph:
            pycallgraph.make_dot_graph('test_homepage_bench.png')
        print ' ... {0:.1f} ms/view '.format((t / self.n) * 1000),
        sys.stdout.flush()

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
