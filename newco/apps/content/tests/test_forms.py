from django.utils import unittest
from django.test.client import RequestFactory, Client
from django.forms import CharField
from django.contrib.auth.models import User, AnonymousUser
from ..models import Item
from ..forms import ItemForm, DictionaryField, KeyValueField


class SimpleTest(unittest.TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.client = Client()
        self.request = self.factory.get('/')
        self.request.user = AnonymousUser()

    def test_dictionary_field(self):
        '''
        Content: test DictionaryField
        '''
        payload = {"data_0_0": "_class",
                   "data_0_1": "product",
                   "data_1_0": "name",
                   "data_1_1": "something awesome",
                   "data_2_0": "www",
                   "data_2_1": "zzz"}
        expected_output = {'data': {u'_class': u'product',
                                    u'name': u'something awesome',
                                    u'www': u'zzz'}}
        request = self.factory.post('/add/item/', payload)
        request.user = User.objects.get(id=1)
        form = ItemForm(**{'data': payload, 'request': request})
        assert form.is_bound
        assert form.is_valid()
        self.assertEqual(form.cleaned_data, expected_output)

        form = ItemForm(request=request, initial=Item.initial)
        assert not form.is_valid()

        field = DictionaryField(fields=(CharField, CharField))
        data = {"VENEZUELA": "CARACAS", "CANADA": "TORONTO"}
        self.assertEqual(field.compress(field.widget.decompress(data)), data)

    def test_keyvalue_field(self):
        '''
        Content: test KeyValueField
        '''
        kvf = KeyValueField(fields=(CharField, CharField))
        pair = ('a', 'b')
        self.assertEquals(kvf.compress(kvf.widget.decompress(pair)), pair)
