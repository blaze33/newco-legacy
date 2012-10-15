import json
from django.forms import Widget
from django.utils.safestring import mark_safe
from django.forms.widgets import flatatt
from django.contrib.admin.widgets import AdminTextareaWidget
from django.utils.html import escape


def _to_python(value):
    return json.loads(value)


def _to_text(value):
    return json.dumps(value, sort_keys=True, indent=2)


class JsonPairInputs(AdminTextareaWidget):
    """A widget that displays JSON Key Value Pairs
    as a list of text input box pairs

    Usage (in forms.py) :
    examplejsonfield = forms.CharField(label  = "Example JSON Key Value Field", required = False,
                                       widget = JsonPairInputs(val_attrs={'size':35},
                                                               key_attrs={'class':'large'}))

    """

    def __init__(self, *args, **kwargs):
        """A widget that displays JSON Key Value Pairs
        as a list of text input box pairs

        kwargs:
        key_attrs -- html attributes applied to the 1st input box pairs
        val_attrs -- html attributes applied to the 2nd input box pairs

        """
        self.key_attrs = {}
        self.val_attrs = {}
        if "key_attrs" in kwargs:
            self.key_attrs = kwargs.pop("key_attrs")
        if "val_attrs" in kwargs:
            self.val_attrs = kwargs.pop("val_attrs")
        Widget.__init__(self, *args, **kwargs)

    def render(self, name, value, attrs=None):
        """Renders this widget into an html string

        args:
        name  (str)  -- name of the field
        value (str)  -- a dictionary automatically passed in by django
        attrs (dict) -- automatically passed in by django (unused in this function)
        """

        pair_template = '''
        <input type="text" name="json_key[{fieldname}]" value="{key}" {key_attrs}>
        <input type="text" name="json_value[{fieldname}]" value="{value}" {val_attrs}>
        <br>'''
        ret = '<div class="control-group" id="form_data">'
        if value:
            for k, v in value.items():
                ctx = {'key': escape(k),
                       'value': escape(v),
                       'fieldname': name,
                       'key_attrs': flatatt(self.key_attrs),
                       'val_attrs': flatatt(self.val_attrs)}
                ret += pair_template.format(**ctx)
        ret += '</div>'
        return mark_safe(ret)

    def value_from_datadict(self, data, files, name):
        """
        Returns the simplejson representation of the key-value pairs
        sent in the POST parameters

        args:
        data  (dict)  -- request.POST or request.GET parameters
        files (list)  -- request.FILES
        name  (str)   -- the name of the field associated with this widget

        """
        datadict = "null"
        if ('json_key[%s]' % name) and ('json_value[%s]' % name) in data:
            keys     = data.getlist("json_key[%s]" % name)
            values   = data.getlist("json_value[%s]" % name)
            datadict = {}
            for key, value in zip(keys, values):
                if len(key) > 0:
                    datadict[key] = value
        return _to_text(datadict)

    class Media:
        # css = {
        #          'all': ('/css/pretty.css',),
        #     }
        js = ('js/widget.js',)
