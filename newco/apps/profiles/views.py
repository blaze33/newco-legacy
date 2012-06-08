from idios.views import ProfileDetailView

from items.models import Question, Answer
from profiles.models import Reputation


class MyProfileDetailView(ProfileDetailView):

    def get_context_data(self, **kwargs):
        context = super(MyProfileDetailView, self).get_context_data(**kwargs)
        context['questions'] = Question.objects.filter(author=self.object.user)
        context['answers'] = Answer.objects.filter(author=self.object.user)
        context['reputation'] = Reputation.objects.get(user=self.object.user)

        return context
