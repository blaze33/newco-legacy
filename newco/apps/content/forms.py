from django.forms import ModelForm
from content.models import Item


class ItemForm(ModelForm):

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