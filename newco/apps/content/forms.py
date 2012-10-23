from __future__ import unicode_literals
from django.forms import ModelForm, MultiValueField, MultiWidget, CharField, DecimalField
from content.models import Item, Relation


class KeyValueWidget(MultiWidget):

    def render(self, name, value, attrs=None):
        out = super(KeyValueWidget, self).render(name, value, attrs)
        return '{0}<br>'.format(out)

    def decompress(self, value):
        return value


class KeyValueField(MultiValueField):
    widget = KeyValueWidget

    def __init__(self, fields=(), *args, **kwargs):
        widgets = (f.widget for f in fields)
        self.widget = self.widget(widgets)
        return super(KeyValueField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        return data_list if data_list and data_list[0] else None


class DictionaryWidget(MultiWidget):

    def decompress(self, value):
        return value.items()

    class Media:
        css = {
                 'all': ('css/widget.css',),
            }
        js = ('js/widget.js',)


class DictionaryField(MultiValueField):
    widget = DictionaryWidget

    def __init__(self, fields=(), *args, **kwargs):
        widgets = (f.widget for f in fields)
        self.widget = self.widget(widgets)
        return super(DictionaryField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        '''
        Concatenate key/value pairs into a dictionary.
        '''
        return dict([x for x in data_list if x != None])


class ItemForm(ModelForm):

    data = DictionaryField
    create = False

    def __init__(self, *args, **kwargs):
        if 'instance' not in kwargs or kwargs['instance'] == None:
            self.create = True
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
            self.user = self.request.user
        data_field = self.data  # because self.data will be overwritten
        super(ItemForm, self).__init__(*args, **kwargs)
        kvf = KeyValueField(fields=(CharField(), CharField()))
        # counting how many key/value pairs we have to deal with
        l1, l2 = 0, 0
        if 'data' in self.initial:
            l1 = len(self.initial['data'])
        if 'data' in kwargs:
            n = 0
            for i in kwargs['data']:
                if 'data_' in i:
                    n += 1
                l2 = n / 2
        fields = [kvf] * max(l1, l2)
        self.fields['data'] = data_field(fields=fields)

    class Meta:
        model = Item
        exclude = ('successors')


class RelationForm(ItemForm):
    class Meta:
        model = Relation
