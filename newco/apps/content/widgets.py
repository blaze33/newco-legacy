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

import simplejson 
from django.forms import Widget
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.forms.widgets import flatatt
from django.contrib.admin.widgets import AdminTextareaWidget

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
        value (str)  -- a json string of a two-tuple list automatically passed in by django
        attrs (dict) -- automatically passed in by django (unused in this function)
        """
        
        ret = ''
        if value and len(value) > 0: 
            for k,v in value.items(): 
                ctx = {'key':k,
                       'value':v,
                       'fieldname':name,
                       'key_attrs': flatatt(self.key_attrs),
                       'val_attrs': flatatt(self.val_attrs) }
                ret += '<input type="text" name="json_key[%(fieldname)s]" value="%(key)s" %(key_attrs)s> <input type="text" name="json_value[%(fieldname)s]" value="%(value)s" %(val_attrs)s><br />' % ctx
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
        if data.has_key('json_key[%s]' % name) and data.has_key('json_value[%s]' % name): 
            keys     = data.getlist("json_key[%s]" % name) 
            values   = data.getlist("json_value[%s]" % name) 
            datadict = {}
            for key, value in zip(keys, values): 
                if len(key) > 0:
                    datadict[key]=value
            print datadict
        return _to_text(datadict)

    class Media:
        # css = {
        #          'all': ('/css/pretty.css',),
        #     }
        js = ('js/widget.js',)