from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.contrib.auth.models import User
from django.views.generic.simple import direct_to_template
from django.views.generic.edit import ProcessFormView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.urlresolvers import reverse
from idios.views import ProfileDetailView, ProfileListView
import json

from items.models import Item, Content
from profiles.models import Profile
from follow.models import Follow
from utils.followtools import process_following
from utils.tools import load_object


class ProfileProcessFormView(ProcessFormView):

    def post(self, request, *args, **kwargs):
        if 'pf_pick' in request.POST:
            name = request.POST['pf_pick']
            profile_list = Profile.objects.filter(name=name)
            if profile_list.count() == 1:
                response = profile_list[0].get_absolute_url()
            else:
                response = reverse("profile_list") + "?search=" + name
            return HttpResponseRedirect(response)
        else:
            return super(ProfileProcessFormView, self).post(request,
                                                            *args, **kwargs)


class ProfileDetailView(ProfileDetailView, ProfileProcessFormView):

    is_profile_page = True
    
    demo_dashboard = False ## For demo only line to be deleted ##

    demo_feed = False ## For demo only line to be deleted ##
    demo_dashboard_contrib = False ## For demo only line to be deleted ##
    demo_collaboration = False ## For demo only line to be deleted ##
    demo_draft = False ## For demo only line to be deleted ##
    demo_allcontrib = False ## For demo only line to be deleted ##
    demo_shopping_notes = False ## For demo only line to be deleted ##
    demo_purchase_history = False ## For demo only line to be deleted ##
    
    def dispatch(self, request, *args, **kwargs):
        if self.is_profile_page:
            profile = Profile.objects.get(pk=kwargs.pop('pk'))
            if profile.slug and kwargs['slug'] != profile.slug:
                url = profile.get_absolute_url()
                return HttpResponsePermanentRedirect(url)
            kwargs['username'] = profile.user.username
        return super(ProfileDetailView, self).dispatch(request,
                                                        *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if self.is_profile_page:
            if self.demo_feed:  ## For demo only line to be deleted ##
                self.template_name = "idios/profile_demo_feed.html"  ## For demo only line to be deleted ##
            elif self.demo_dashboard_contrib:  ## For demo only line to be deleted ##
                self.template_name = "idios/profile_demo_dashboard_contrib.html"  ## For demo only line to be deleted ##
            elif self.demo_collaboration:  ## For demo only line to be deleted ##
                self.template_name = "idios/profile_demo_collaboration.html"  ## For demo only line to be deleted ##
            elif self.demo_draft:  ## For demo only line to be deleted ##
                self.template_name = "idios/profile_demo_draft.html"  ## For demo only line to be deleted ##
            elif self.demo_allcontrib:  ## For demo only line to be deleted ##
                self.template_name = "idios/profile_demo_allcontrib.html"  ## For demo only line to be deleted ## 
            elif self.demo_shopping_notes:  ## For demo only line to be deleted ##
                self.template_name = "idios/profile_demo_shopping_notes.html"  ## For demo only line to be deleted ##                
            elif self.demo_purchase_history:  ## For demo only line to be deleted ##
                self.template_name = "idios/profile_demo_purchase_history.html"  ## For demo only line to be deleted ##                

            elif self.demo_dashboard:  ## For demo only line to be deleted ##
                self.template_name = "idios/profile_demo.html"  ## For demo only line to be deleted ##
               
            #self.template_name = "profiles/profile.html"
            return super(ProfileDetailView, self).get(self,
                                                    request,
                                                    *args,
                                                    **kwargs)
        elif request.user.is_authenticated():
            self.template_name = "profiles/profile_homepage.html"
            self.page_user = request.user
            self.object = self.page_user.get_profile()
            context = self.get_context_data()
            context.update({'kwargs': kwargs})
            return self.render_to_response(context)
        else:
            return direct_to_template(request, "homepage.html")

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

        profiles = Profile.objects.order_by("name").distinct("name")
        list_pf = list(profiles.values_list('name', flat=True))

        context = super(ProfileDetailView, self).get_context_data(**kwargs)
        context.update({
            'reputation': self.page_user.reputation,
            'history': history.select_subclasses(),
            'drafts': drafts.select_subclasses(),
            'fwers': User.objects.filter(pk__in=fwers_ids),
            'fwees': User.objects.filter(pk__in=fwees_ids),
            'items_fwed': Item.objects.filter(pk__in=items_fwed_ids),
            'newsfeed': feed.select_subclasses(),
            'data_source_profile': json.dumps(list_pf)
        })
        
        allcontrib_feed = Content.objects.filter( ## For demo only line to be deleted ##
                Q(author=self.page_user) ## For demo only line to be deleted ##
        ) ## For demo only line to be deleted ##
        
        context.update({ ## For demo only line to be deleted ##

            'demo_feed': self.demo_feed, ## For demo only line to be deleted ##
            'demo_dashboard_contrib': self.demo_dashboard_contrib, ## For demo only line to be deleted ##
            'demo_draft': self.demo_draft, ## For demo only line to be deleted ##
            'demo_allcontrib': self.demo_allcontrib, ## For demo only line to be deleted ##
            'demo_shopping_notes': self.demo_shopping_notes, ## For demo only line to be deleted ##
            'demo_purchase_history': self.demo_purchase_history, ## For demo only line to be deleted ##
            'demo_dashboard': self.demo_dashboard, ## For demo only line to be deleted ##
            'is_profile_page': self.is_profile_page,
            'allcontrib_feed': allcontrib_feed.select_subclasses(),  ## For demo only line to be deleted ##
        })

        return context

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        if 'follow' in request.POST or 'unfollow' in request.POST:
            obj = load_object(request)
            success_url = request.path
            return process_following(request, obj, success_url)
        else:
            return super(ProfileDetailView, self).post(request,
                                                            *args, **kwargs)


class ProfileListView(ProfileListView, ProfileProcessFormView):

    def get_queryset(self):
        profiles = self.get_model_class().objects.select_related()

        search_terms = self.request.GET.get("search", "")
        order = self.request.GET.get("order", "")

        if search_terms:
            profiles = profiles.filter(name__icontains=search_terms)
        if order == "date":
            profiles = profiles.order_by("-user__date_joined")
        elif order == "name":
            profiles = profiles.order_by("user__username")

        return profiles

    def get_context_data(self, **kwargs):
        list_pf = list(Profile.objects.all().values_list('name', flat=True))

        context = super(ProfileListView, self).get_context_data(**kwargs)
        context.update({'data_source_profile': json.dumps(list_pf)})
        return context
