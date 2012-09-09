#from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.contrib.auth.models import User
#from django.views.generic.simple import direct_to_template
#from django.utils.decorators import method_decorator
#from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.urlresolvers import reverse
from idios.views import ProfileDetailView, ProfileListView
import json

## Seb: faire le nettoyage dans les import !

from profiles.views import ProfileProcessFormView
from items.models import Item, Content
from profiles.models import Profile
from follow.models import Follow
from taggit.models import Tag
#from utils.followtools import process_following
#from utils.tools import load_object


class DashboardView(ProfileDetailView, ProfileProcessFormView):

    dashboard = False
    feed = False

    contrib = False
    collaboration = False
    drafts = False
    all_contrib = False

    shop_notes = False
    purch_histo = False

    demo_profile = False ## For demo only line to be deleted ##
    
    
    def get(self, request, *args, **kwargs):
        if self.dashboard: self.template_name = "dashboard/dashboard.html"
        elif self.feed: self.template_name = "dashboard/db_feed.html"
        
        elif self.contrib: self.template_name = "dashboard/db_contrib.html"
        elif self.collaboration: self.template_name = "dashboard/db_collaboration.html"
        elif self.drafts: self.template_name = "dashboard/db_drafts.html"
        elif self.all_contrib: self.template_name = "dashboard/db_all_contrib.html" 
        
        elif self.shop_notes: self.template_name = "dashboard/db_shopping_notes.html"                
        elif self.purch_histo: self.template_name = "dashboard/db_purchase_history.html"                

        elif self.demo_profile: self.template_name = "dashboard/db_profile.html"


        self.page_user = request.user
        self.object = self.page_user.get_profile()
        context = self.get_context_data()
        context.update({'kwargs': kwargs})
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        #TODO: better handling of QueryManager

        history = Content.objects.filter(
                Q(author=self.page_user) & Q(status=Content.STATUS.public)
        )
        drafts = Content.objects.filter(
                Q(author=self.page_user) & Q(status=Content.STATUS.draft)
        )

        fwers_ids = Follow.objects.get_follows(
                self.page_user).values_list('user_id', flat=True)
        obj_fwed = Follow.objects.filter(user=self.page_user)
        fwees_ids = obj_fwed.values_list('target_user_id', flat=True)
        items_fwed_ids = obj_fwed.values_list('target_item_id', flat=True)

        feed = Content.objects.filter(
                Q(author__in=fwees_ids) | Q(items__in=items_fwed_ids),
                ~Q(author=self.page_user), status=Content.STATUS.public
        )

        all_contrib_feed = Content.objects.filter(Q(author=self.page_user))

        profile = Profile.objects.get(user=self.page_user)
        skills_list = profile.skills.all()
        items_skills_tag_list = Item.objects.filter(Q(tags__in=skills_list))
        contrib_feed = Content.objects.filter(items__in=items_skills_tag_list)


        profiles = Profile.objects.order_by("name").distinct("name")
        list_pf = list(profiles.values_list('name', flat=True))


        ######
        # boxes:
        # Seb: target here is to prepare for having these boxes customized by user : 'I want to see this in my dashboard, and that, and configure it this way'
        # Next step will be when we'll have hstore ! (useless to do something for 3 weeks)
        boxes_list = [
            #"feed": 
            {
                "title": "Your feed",
                "subtitle": "Mini feed from what you follow",
                "name": "feed",
                "feed": feed.select_subclasses(),
                "mini_feed": "True",
                "slicing": ":4",
                "url_linked_page": reverse("db_feed"),
            },
            #"contrib": 
            {
                "title": "Contribution center",
                "subtitle": "Latest activity on your skills tags... Maybe you'd like to contribute?",
                "name": "contrib",
                "feed": contrib_feed.select_subclasses(),
                "mini_feed": "True",
                "slicing": ":4",
                "url_linked_page": reverse("contrib"),
            },
            #"drafts": 
            {
                "title": "Drafts",
                "subtitle": "Maybe you want to complete and/or publish some?",
                "name": "drafts",
                "feed": drafts.select_subclasses(),
                "mini_feed": "True",
                "slicing": ":4",
                "url_linked_page": reverse("drafts"),
            },
            #"all_contrib": 
            {
                "title": "All contributions",
                "subtitle": "Your latest contributions",
                "name": "all_contrib",
                "feed": all_contrib_feed.select_subclasses(),
                "mini_feed": "True",
                "slicing": ":4",
                "url_linked_page": reverse("all_contrib"),
            },
            
        ]
        ######

        context = super(DashboardView, self).get_context_data(**kwargs)
        context.update({ ## Seb: some context variable are doublon with the 'boxes' : I wait sometime to know how to organize clearly on this
            'reputation': self.page_user.reputation,
            'history_feed': history.select_subclasses(),
            'drafts_feed': drafts.select_subclasses(),
            'fwers': User.objects.filter(pk__in=fwers_ids),
            'fwees': User.objects.filter(pk__in=fwees_ids),
            'items_fwed': Item.objects.filter(pk__in=items_fwed_ids),
            'newsfeed': feed.select_subclasses(),
            'data_source_profile': json.dumps(list_pf),

            'on_dashboard': self.dashboard,
            'on_feed': self.feed, ## For demo only line to be deleted ##
            'on_contrib': self.contrib, ## For demo only line to be deleted ##
            'on_collaboration': self.collaboration, ## For demo only line to be deleted ##
            'on_drafts': self.drafts, ## For demo only line to be deleted ##
            'on_all_contrib': self.all_contrib, ## For demo only line to be deleted ##
            'on_shop_notes': self.shop_notes, ## For demo only line to be deleted ##
            'on_purch_histo': self.purch_histo, ## For demo only line to be deleted ##
            'all_contrib_feed': all_contrib_feed.select_subclasses(),  ## For demo only line to be deleted ##
            'contrib_feed': contrib_feed.select_subclasses(), #.select_subclasses(),
            'boxes_list': boxes_list,
        })

        return context
