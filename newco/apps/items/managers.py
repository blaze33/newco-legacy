from django.db import models
from django.db.models import Q, Sum, Count
from django.db.models.query import QuerySet

from follow.models import Follow
from generic_aggregation import generic_annotate
from model_utils.managers import InheritanceQuerySet, InheritanceManager
from voting.models import Vote

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

    def order_queryset(self, option):
        if option == "popular":
            return generic_annotate(
                self, Vote, Sum('votes__vote')).order_by("-score")
        elif "pub_date" in option:
            return self.order_by(option)
        elif option == "no_answers":
            return self.annotate(score=Count("answer")).filter(score__lte=0)
        return self

    def get_scores_and_votes(self, user):
        scores = Vote.objects.get_scores_in_bulk(self)
        votes = Vote.objects.get_for_user_in_bulk(self, user)
        return [scores, votes]

    def get_qs_tools(self, option, user):
        qs = self.order_queryset(option)
        scores, votes = qs.get_scores_and_votes(user)
        return {"queryset": qs.select_subclasses(),
                "scores": scores, "votes": votes}


class ContentManager(InheritanceManager):
    def get_query_set(self):
        qs = ContentQuerySet(self.model)
        return qs.filter(Q(link__isnull=True) & Q(feature__isnull=True))

    def get_feed(self, user):
        return self.get_query_set().get_feed(user)

    def get_related_contributions(self, user, item_qs):
        return self.get_query_set().get_related_contributions(user, item_qs)

    def order_queryset(self, option):
        return self.get_query_set().order_queryset(option)

    def get_scores_and_votes(self, user):
        return self.get_query_set().get_scores_and_votes(user)
