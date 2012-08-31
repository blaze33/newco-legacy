from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.contrib.auth.models import User
from django.views.generic.simple import direct_to_template
from django.views.generic.edit import ProcessFormView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.urlresolvers import reverse
from profiles.views import ProfileDetailView
#from django.views.generic import DetailView
from follow.models import Follow
import json

from items.models import Item, Content, Question
from profiles.models import Profile
import operator


class DetailView(ProfileDetailView):

    is_profile_page = True
    model = Item

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

        obj_fwed = Follow.objects.filter(user=self.page_user)
        fwees_ids = obj_fwed.values_list('target_user_id', flat=True)
        items_fwed_ids = obj_fwed.values_list('target_item_id', flat=True)

        feed = Content.objects.filter(
                Q(author__in=fwees_ids) | Q(items__in=items_fwed_ids),
                ~Q(author=self.page_user), status=Content.STATUS.public
        )
        feed_all = Content.objects.filter(
               status=Content.STATUS.public
        )
        
        item_pop_dict={'item':-1}
        for item in Item.objects.all():
            questions = Question.objects.filter(
                    Q(items__id=item.id) & Q(status=Content.STATUS.public)
                )
            item_pop_dict[item]=len(questions)
            
        sorted_item_pop_dict = sorted(item_pop_dict.iteritems(), key=operator.itemgetter(1), reverse=True )
        items_list_pop=[]
        element =list(range(10))
        for i in element:
            items_list_pop.append(sorted_item_pop_dict[i][0])
        
#        kwargs.update({'object_list': feed})
#        self.object_list = feed    
        context = super(ProfileDetailView, self).get_context_data(**kwargs)
        
        if 'category_name' in self.kwargs:
            if self.kwargs['category_name']=="newsfeed":
                context['newsfeed_source']=feed_all.select_subclasses()
                context['is_newsfeed']=1
            elif self.kwargs['category_name']=="filtered_newsfeed":
                context['newsfeed_source']=feed.select_subclasses()
                context['is_newsfeed']=1
            elif self.kwargs['category_name']=="popular":
                context['newsfeed_source']=items_list_pop
            elif self.kwargs['category_name']=="last":
                context['newsfeed_source']=Item.objects.all().order_by("-pub_date")
            else:
                context['newsfeed_source']=items_list_pop
        else:
            context['newsfeed_source']=items_list_pop
        
        return context
