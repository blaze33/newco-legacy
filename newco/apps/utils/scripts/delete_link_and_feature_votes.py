from django.contrib.contenttypes.models import ContentType

from voting.models import Vote

from items.models import Content

content_ctype = ContentType.objects.get_for_model(Content)


for v in Vote.objects.all():
    if v.object is None:
        if v.content_type == content_ctype:
            v.delete()
