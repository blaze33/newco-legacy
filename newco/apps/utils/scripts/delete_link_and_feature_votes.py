from django.contrib.contenttypes.models import ContentType

from items.models import Content
from utils.voting import Vote

content_ctype = ContentType.objects.get_for_model(Content)


for v in Vote.objects.all():
    if v.object is None:
        if v.content_type == content_ctype:
            v.delete()
