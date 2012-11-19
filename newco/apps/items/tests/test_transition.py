from django.utils import unittest
from ..models import Item


class SimpleTest(unittest.TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        pass

    def test_fetch_images(self):
        '''
        Items|transition with content: test fetch_images with empty queryset
        '''
        empty_qs = Item.objects.filter(pk=-1)
        self.assertEqual(empty_qs.fetch_images(), {})
