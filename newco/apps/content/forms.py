from django.forms import ModelForm, Field
from content.models import Item, Relation
from content.widgets import JsonPairInputs, _to_python


class DictionaryField(Field):
    """A dictionary form field."""

    def __init__(self, **params):
        super(DictionaryField, self).__init__(**params)

    def to_python(self, value):
        print "to_python ", value
        print _to_python(value)
        return _to_python(value)


class ItemForm(ModelForm):

    data = DictionaryField(label="HStore Key Value Field", required=False,
                           widget=JsonPairInputs())
    create = False

    def __init__(self, *args, **kwargs):
        if 'instance' not in kwargs or kwargs['instance'] == None:
            self.create = True
            self.request = kwargs.pop('request')
            self.user = self.request.user
        return super(ItemForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Item
        exclude = ('successors')


class RelationForm(ItemForm):
    class Meta:
        model = Relation
