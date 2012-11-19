from django.utils import unittest
from items.models import Item


class SimpleTest(unittest.TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        pass

    def test_fetch_images(self):
        '''
        Content|transition: test fetch_images
        '''
        empty_qs = Item.objects.filter(pk=-1)
        self.assertEqual(empty_qs.fetch_images(), {})
