from idios.views import ProfileDetailView

from items.models import Question, Answer


class MyProfileDetailView(ProfileDetailView):

    def get_context_data(self, **kwargs):
        context = super(MyProfileDetailView, self).get_context_data(**kwargs)
        context['questions'] = Question.objects.filter(user=self.object.user)
        context['answers'] = Answer.objects.filter(user=self.object.user)

        return context
