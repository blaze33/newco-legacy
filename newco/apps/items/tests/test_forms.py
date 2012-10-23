# import json
from django.conf import settings
from django.utils import unittest
from django.test.client import RequestFactory, Client
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User, AnonymousUser
# from ..models import Item
from ..forms import ItemForm
# from items.views import ContentCreateView, ContentDeleteView, ContentDetailView



from django.http import HttpResponse

class SimpleTest(unittest.TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.client = Client()
        self.request = self.factory.get('/')
        self.request.user = AnonymousUser()
        # self.views = [ContentCreateView, ContentDeleteView, ContentDetailView]

    def test_form(self):
    	'''
    	Content: test forms return the good HttpResponse + good next page
    	'''
    	#assert isinstance(ContentCreateView.post(self.request),HttpResponse)
    	assert 1 == 1
    	assert 1 == 2
