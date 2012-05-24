from django.views.generic import View, DetailView, CreateView
from django.views.generic import UpdateView, DeleteView
from django.core.urlresolvers import reverse
from django.http import Http404
from django.db.models.loading import get_model

from items.models import Item, Question
from items.forms import QuestionForm, AnswerForm, StoryForm

app_name = 'items'


class ContentView(View):
    def dispatch(self, request, *args, **kwargs):
        self.model = get_model(app_name, kwargs['model_name'])
        return super(ContentView, self).dispatch(request, *args, **kwargs)


class ContentCreateView(ContentView, CreateView):

    def form_valid(self, form):
        model_name = self.model.__name__
        self.object = form.save(commit=False)

        if self.request.user.is_authenticated():
            self.object.user = self.request.user

        if model_name in {"Question", "Story"}:
            item_id = self.request.POST['item_id']
            self.object.item = Item.objects.get(pk=item_id)
        elif model_name == "Answer":
            question_id = self.request.POST['question_id']
            self.object.question = Question.objects.get(pk=question_id)

        return super(ContentCreateView, self).form_valid(form)

    def get_template_names(self):
        names = super(ContentCreateView, self).get_template_names()

        model_name = self.model.__name__
        if model_name in {"Question", "Story"}:
            names.append("items/item_detail.html")

        return names

    def get_context_data(self, **kwargs):
        context = super(ContentCreateView, self).get_context_data(**kwargs)

        model_name = self.model.__name__
        if model_name == "Answer" and "answer_form" in self.request.POST:
            question_id = self.request.POST['question_id']
            context['question'] = Question.objects.get(pk=question_id)
            context['form'] = AnswerForm()
        elif model_name in {"Question", "Story"} and \
                ("add_question" in self.request.POST or "add_story" in self.request.POST):
            item_id = self.request.POST['item_id']
            context['item'] = Item.objects.get(pk=item_id)
            if "add_question" in self.request.POST:
                context['question_form'] = QuestionForm(self.request.POST)
                context['story_form'] = StoryForm()
            elif "add_story" in self.request.POST:
                context['question_form'] = QuestionForm()
                context['story_form'] = StoryForm(self.request.POST)

        return context


class ContentUpdateView(ContentView, UpdateView):

    def get_template_names(self):
        model_name = self.model.__name__
        if model_name == "Item":
            return ("items/item_form.html")
        elif model_name == "Question":
            return ("items/question_edit_form.html")
        elif model_name == "Answer":
            return ("items/answer_form.html")
        elif model_name == "Story":
            return ("items/story_edit_form.html")

    # Check if necessary
    def get_success_url(self):
        model_name = self.model.__name__
        if model_name == "Item":
            return self.object.get_absolute_url()
        elif model_name in {"Question", "Story"}:
            return self.object.item.get_absolute_url()
        elif model_name == "Answer":
            return self.object.question.item.get_absolute_url()
        else:
            return super(ContentUpdateView, self).get_success_url(self)

    def get_context_data(self, **kwargs):
        context = super(ContentUpdateView, self).get_context_data(**kwargs)
        model_name = self.model.__name__
        if model_name in {"Question", "Story"}:
            context['item'] = self.object.item
        elif model_name == "Answer":
            context['question'] = self.object.question

        return context


class ContentDeleteView(ContentView, DeleteView):

    template_name = "items/item_confirm_delete.html"

    def get_success_url(self):
        model_name = self.model.__name__
        if model_name == "Item":
            return reverse("item_index")
        elif model_name in {"Question", "Story"}:
            return self.object.item.get_absolute_url()
        elif model_name == "Answer":
            return self.object.question.item.get_absolute_url()
        else:
            return reverse("item_index")

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(ContentDeleteView, self).get_object()
#        if obj.user and not obj.user == self.request.user:
#            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super(ContentDeleteView, self).get_context_data(**kwargs)
        context['model_name'] = self.model.__name__

        if context['model_name'] == "Item":
            context['item'] = self.object
        elif context['model_name'] in {"Question", "Story"} :
            context['item'] = self.object.item
        elif context['model_name'] == "Answer":
            context['item'] = self.object.question.item

        return context


class ItemDetailView(DetailView):

    queryset = Item.objects.all()

    def get_context_data(self, **kwargs):
        context = super(ItemDetailView, self).get_context_data(**kwargs)
        if not self.request.POST:
            context['question_form'] = QuestionForm()
            context['story_form'] = StoryForm()
        return context
