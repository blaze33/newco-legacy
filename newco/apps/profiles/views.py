from django.contrib.auth.models import User

from idios.views import ProfileDetailView

from items.models import Question, Answer
from profiles.models import Reputation
from follow.models import Follow
from profiles.models import Profile

class MyProfileDetailView(ProfileDetailView):

    def get_context_data(self, **kwargs):
        context = super(MyProfileDetailView, self).get_context_data(**kwargs)
        context['questions'] = Question.objects.filter(author=self.object.user)
        context['answers'] = Answer.objects.filter(author=self.object.user)
        context['reputation'] = Reputation.objects.get(user=self.object.user)
        followers_links = Follow.objects.get_follows(self.object.user)
        followers_ids = [f['user_id'] for f in followers_links.values()]
        context['followers_ids'] = followers_ids
        context['followers'] = User.objects.filter(pk__in=followers_ids)
        
        #content ordering for newsfeed inversed
        questions = Question.objects.filter(author__in=followers_ids)
        answers = Answer.objects.filter(author__in=followers_ids)
        contents_nfi = list(questions) #nf is for NewsFeed Inversed
        contents_nfi.extend(list(answers))
        context['contents_nfi'] = sorted(contents_nfi, key=lambda c: c.pub_date, reverse=True)        
        
        followed_links = Follow.objects.filter(user=self.object.user)
        followeds_ids = [f['target_user_id'] for f in followed_links.values()]
        context['followeds_ids'] = followeds_ids
        context['followeds'] = User.objects.filter(pk__in=followeds_ids)
        
        #content ordering for newsfeed
        questions = Question.objects.filter(author__in=followeds_ids)
        answers = Answer.objects.filter(author__in=followeds_ids)
        contents_nf = list(questions) #nf is for NewsFeed
        contents_nf.extend(list(answers))
        context['contents_nf'] = sorted(contents_nf, key=lambda c: c.pub_date, reverse=True)

        return context
