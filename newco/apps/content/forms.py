try:
    import yaml
    def _to_python(value):
        return yaml.load(value)
    def _to_text(value):
        return yaml.dump(value, default_flow_style=False)
except ImportError:
    try:
        import json
    except ImportError:
        from django.utils import simplejson as json
    def _to_python(value):
        return json.loads(value)
    def _to_text(value):
        return json.dumps(value, sort_keys=True, indent=2)

from django.forms import ModelForm, Field, CharField
from content.models import Item
from content.widgets import JsonPairInputs

class DictionaryField(Field):
    """A dictionary form field."""

    def __init__(self, **params):
        params['widget'] = JsonPairInputs
        super(DictionaryField, self).__init__(**params)

    def to_python(self, value):
        return _to_python(value)

class ItemForm(ModelForm):

    data = DictionaryField(label  = "HStore Key Value Field", required = False,
                                   widget = JsonPairInputs(val_attrs={'size':35},
                                                           key_attrs={'class':'large'}))
    create = False

    def __init__(self, *args, **kwargs):
        if 'instance' not in kwargs or kwargs['instance'] == None:
            self.create = True
            self.request = kwargs.pop('request')
            self.user = self.request.user
        return super(ItemForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Item
        exclude = ('context')