import glob
import re
import string

from django.conf import settings
from django.template.base import TemplateDoesNotExist
from django.template.loader import find_template_loader
from django.utils.datastructures import SortedDict

FILE_PATTERN = "(?P<path>.*/)(?P<filename>\w+)\.(?P<extension>\w+)$"
TITLE_PATTERN = "{# TITLE: (?P<title>.+) #}"


def get_template(template_name):
    loaders = []
    for loader_name in settings.TEMPLATE_LOADERS:
        loader = find_template_loader(loader_name)
        if loader is not None:
            loaders.append(loader)
    template_source_loaders = tuple(loaders)
    for loader in template_source_loaders:
        try:
            return loader.load_template_source(template_name)
        except TemplateDoesNotExist:
            pass

    return ["", ""]


def get_similar_templates(local_template_path, file_pattern="[1-999]"):
    """
    Looks for templates with similar name pattern. Returns a list
    """
    names = [local_template_path]
    template, source = get_template(names[0])
    tpl_folder = re.match("(?P<global_path>.*)" + names[0],
                          source).group("global_path")
    m = re.match(FILE_PATTERN, source)
    pattern = string.join(m.group("path", "filename"), "") + \
        "_" + file_pattern + "." + m.group("extension")
    template_names = glob.glob(pattern)
    names.extend([re.match(tpl_folder + "(?P<name>.*)", tpl).group("name")
                  for tpl in template_names])
    return names


def get_template_titles(template_names):
    """
    Looks for title pattern in each template. Returns a dictionary
    """
    templates = SortedDict()
    for name in template_names:
        template, source = get_template(name)
        m = re.search(TITLE_PATTERN, template)
        title = m.group("title") if m else name
        templates.update({name: title})
    return templates
