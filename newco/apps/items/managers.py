from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet

from follow.models import Follow
from model_utils.managers import InheritanceQuerySet, InheritanceManager

from content.models import Item


class ItemQuerySet(QuerySet):
    def fetch_images(self):
        """
        Add the corresponding image object to 'image' property
        """
        ids = [i.id for i in self]
        if len(ids) == 0:
            return {}
        nodes = Item.objects.hfilter(
            {'_class': 'product'}).extra(
                where=["(content_item.data -> 'legacy_id') IN (%s)"
                       % ', '.join('%s' for x in ids)],
                params=map(unicode, ids)).hselect(['legacy_id'])
        match = (len(nodes) == self.count())
        ids_table = {}
        for obj in self:
            obj.node = [n for n in nodes if int(n.legacy_id) == obj.id][0] \
                if match else obj.node
            ids_table.update({obj.node.id: obj.id})

        images_qs = Item().graph.get_images(ids=ids_table.keys()).extra(
            select={'item_id': 'T4.from_item_id'})
        for i in images_qs:
            for obj in self:
                if obj.id == ids_table[i.item_id]:
                    obj.image = i
        return self


class ItemManager(models.Manager):
    def get_query_set(self):
        return ItemQuerySet(self.model)

    def fetch_images(self):
        return self.get_query_set().fetch_images()


class ContentQuerySet(InheritanceQuerySet):
    def get_feed(self, user):
        """
        Get the newsfeed of a specific user
        """
        obj_fwed = Follow.objects.filter(user=user)
        fwees_ids = obj_fwed.values_list('target_user_id', flat=True)
        items_fwed_ids = obj_fwed.values_list('target_item_id', flat=True)

        return self.filter(
            Q(author__in=fwees_ids) | Q(items__in=items_fwed_ids),
            ~Q(author=user), status=self.model.STATUS.public
        )

    def get_related_contributions(self, user, item_qs):
        profile = user.get_profile()
        item_qs = item_qs.filter(tags__in=profile.skills.all())
        return self.filter(items__in=item_qs)


class ContentManager(InheritanceManager):
    def get_query_set(self):
        qs = ContentQuerySet(self.model)
        return qs.filter(Q(link__isnull=True) & Q(feature__isnull=True))
