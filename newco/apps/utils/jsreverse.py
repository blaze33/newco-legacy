import re
import os
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import render_to_response
from django.core import urlresolvers
from django_js_reverse.settings import JS_VAR_NAME


def urls_js():
    url_patterns = urlresolvers.get_resolver(None).reverse_dict.items()
    url_list = [(url_name, url_pattern[0][0]) for url_name, url_pattern in url_patterns if isinstance(url_name, basestring)]
    url_list.sort()
    if not re.match(r'^[$A-Z_][\dA-Z_$]*$', JS_VAR_NAME.upper()):
        raise ImproperlyConfigured('JS_REVERSE_JS_VAR_NAME setting "%s" is not a valid javascript identifier.' % (JS_VAR_NAME))
    return render_to_response('django_js_reverse/urls_js.tpl',
                              {
                                  'urls': url_list,
                                  'js_var_name': JS_VAR_NAME
                              },
                              mimetype='application/javascript'
                              )


def save_static_urls_js(root):
    content = urls_js()
    path = os.path.join(root, "static", "js", "reverse-urls.js")
    with open(path, "w") as f:
        f.write(content.content)
