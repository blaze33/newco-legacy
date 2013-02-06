from django.db import models
from django.db.models import Q, Count, Sum
from django.db.models.query import QuerySet

from model_utils.managers import InheritanceQuerySet, InheritanceManager

from content.models import Item
from items import STATUSES, EMPTY_SCORE
from utils.follow import Follow
from utils.voting import Vote


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

    #### TODO: Take into account products with "score=0" contents ####
    def order_queryset(self, option):
        if option == "popular":
            return self.annotate(count=Count("content__votes__vote"),
                            score=Sum("content__votes__vote")
                        ).filter(count__gt=0).order_by("-score")


class ItemManager(models.Manager):
    def get_query_set(self):
        return ItemQuerySet(self.model)

    def fetch_images(self):
        return self.get_query_set().fetch_images()
    
    def order_queryset(self, option):
        return self.get_query_set().order_queryset()


class ContentQuerySet(InheritanceQuerySet):
    def questions(self):
        return self.filter(question__isnull=False)

    def answers(self):
        return self.filter(answer__isnull=False)

    def get_feed(self, user):
        """
        Get the newsfeed of a specific user
        """
        obj_fwed = Follow.objects.filter(user=user)
        fwees_ids = obj_fwed.values_list("target_user_id", flat=True)
        items_fwed_ids = obj_fwed.values_list("target_item_id", flat=True)

        return self.public().exclude(author=user).filter(
            Q(author__in=fwees_ids) | Q(items__in=items_fwed_ids)).distinct()

    def get_related_contributions(self, user, item_qs):
        profile = user.get_profile()
        item_qs = item_qs.filter(tags__in=profile.skills.all())
        return self.filter(items__in=item_qs)

    def order_queryset(self, option, scores=None):
        if option == "popular":
            if not scores:
                scores = self.get_scores()
            qs = self.select_subclasses()
            return sorted(qs, key=lambda c: scores.get(c.id).get("score"),
                          reverse=True)
        elif "pub_date" in option:
            return self.order_by(option).select_subclasses()
        elif option == "last":
            return self.order_by("-pub_date").select_subclasses()
        elif option in ["no_answers", "unanswered"]:
            return self.annotate(score=Count("question__answer")).filter(
                score__lte=0, status=STATUSES.public).select_subclasses()
        return self

    def get_scores(self, add_related_questions=False):
        if add_related_questions:
            self = self.add_related_questions()
        scores = Vote.objects.get_scores_in_bulk(self)
        for item in self:
            pk = item._get_pk_val()
            if not pk in scores:
                scores.update({pk: EMPTY_SCORE})
        return scores

    def get_votes(self, user):
        return Vote.objects.get_for_user_in_bulk(self, user)

    def get_scores_and_votes(self, user, add_related_questions=False):
        if add_related_questions:
            self = self.add_related_questions()
        return [self.get_scores(False), self.get_votes(user)]

    def add_related_questions(self):
        self = self.distinct()
        question_ids = filter(
            None, self.values_list("answer__question", flat=True))
        question_qs = self.model.objects.filter(id__in=question_ids).distinct()
        return self | question_qs

    def public(self):
        return self.filter(status=STATUSES.public)

    def draft(self):
        return self.filter(status=STATUSES.draft)

    def can_view(self, user):
        if user.is_superuser:
            return self
        query = Q(status=STATUSES.public)
        if user.is_authenticated():
            query = query | Q(author=user)
        return self.filter(query)

    def prefetch_items_image(self, item_model):
        """
        WARNING: it does force the QuerySet to be evaluated
        """
        content_ids = [i.id for i in self]
        items = item_model.objects.filter(
            content__id__in=content_ids).distinct().fetch_images()
        image_dict = dict((item.id, item.image) for item in items)
        for content in self:
            for item in content.items.all():
                item.image = image_dict[item.id]
        return self


class ContentManager(InheritanceManager):
    def get_query_set(self):
        return ContentQuerySet(self.model)

    def questions(self):
        return self.get_query_set().questions()

    def answers(self):
        return self.get_query_set().answers()

    def get_feed(self, user):
        return self.get_query_set().get_feed(user)

    def get_related_contributions(self, user, item_qs):
        return self.get_query_set().get_related_contributions(user, item_qs)

    def order_queryset(self, option):
        return self.get_query_set().order_queryset(option)

    def top_objects_queryset(self):
        return self.get_query_set().top_objects_queryset()

    def get_scores(self, add_related_questions=False):
        return self.get_query_set().get_scores(add_related_questions)

    def get_votes(self, user):
        return self.get_query_set().get_votes(user)

    def get_scores_and_votes(self, user, add_related_questions=False):
        return self.get_query_set().get_scores_and_votes(
            user, add_related_questions)

    def public(self):
        return self.get_query_set().public()

    def draft(self):
        return self.get_query_set().draft()

    def can_view(self, user):
        return self.get_query_set().can_view(user)

    def prefetch_items_image(self, item_model):
        return self.get_query_set().prefetch_items_image(item_model)
