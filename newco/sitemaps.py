from django.contrib.sitemaps import GenericSitemap
from items.models import Item, Question

sections = (Item, Question)
names = {
    Item.__name__.lower(): 'products',
    Question.__name__.lower(): 'questions'
}
all_sitemaps = {}
for section in sections:

    info_dict = {
        'queryset': section.objects.all(),
    }

    sitemap = GenericSitemap(info_dict, priority=0.6)

    # dict key is provided as 'section' in sitemap index view
    all_sitemaps[names[section.__name__.lower()]] = sitemap
