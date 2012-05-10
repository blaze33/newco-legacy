from django.db import models
from django.core.urlresolvers import reverse

from configurableproduct.models import CProduct


class DProduct(CProduct):
    
    class Meta(object):
        proxy = True

    def get_absolute_url(self):
        kwargs = {"product_id": self.id}
        return reverse("product_detail", kwargs=kwargs)
