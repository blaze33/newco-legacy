from django.db.models import Q

from follow.models import Follow
from model_utils.managers import InheritanceQuerySet, InheritanceManager


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
