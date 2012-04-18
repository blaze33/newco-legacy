from django.db import models
from django.utils.translation import ugettext_lazy as _

from configurableproduct.models import CProduct


class DProduct(CProduct):
    
    class Meta(object):
        proxy = True

    def get_absolute_url(self):
        return "/products/%i/" % self.id