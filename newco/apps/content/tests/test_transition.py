from django.utils import unittest
from ..transition import fetch_images
from ..models import Item


class SimpleTest(unittest.TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        pass

    def test_fetch_images(self):
        '''
        Content|transition: test fetch_images
        '''
        empty_qs = Item.objects.filter(pk=-1)
        self.assertEqual(fetch_images(empty_qs), {})
