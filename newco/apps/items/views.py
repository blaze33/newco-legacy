from django.views.generic import View, DetailView, CreateView
from django.views.generic import UpdateView, DeleteView
from django.core.urlresolvers import reverse
from django.http import Http404
from django.db.models.loading import get_model

from items.models import Item
from items.forms import QuestionForm

app_name = 'items'


class ContentView(View):
    def dispatch(self, request, *args, **kwargs):
        self.model = get_model(app_name, kwargs['model_name'])
        return super(ContentView, self).dispatch(request, *args, **kwargs)


class ContentCreateView(ContentView, CreateView):

    def form_valid(self, form):
        self.object = form.save(commit=False)

        if self.request.user.is_authenticated():
            self.object.user = self.request.user

        if self.model.__name__ == "Question":
            item_id = self.request.POST['item_id']
            item = Item.objects.get(pk=item_id)
            self.object.item = item

        return super(ContentCreateView, self).form_valid(form)


class ContentUpdateView(ContentView, UpdateView):

    def get_template_names(self):
        model_name = self.model.__name__
        if model_name == "Question":
            return ("items/question_form_edit.html")
        elif model_name == "Item":
            return ("items/item_form.html")

    def get_success_url(self):
        model_name = self.model.__name__
        if model_name == "Question":
            return self.object.item.get_absolute_url()
        else:
            return super(ContentUpdateView, self).get_success_url(self)

    def get_context_data(self, **kwargs):
        context = super(ContentUpdateView, self).get_context_data(**kwargs)
        model_name = self.model.__name__
        if model_name == "Question":
            context['item'] = self.object.item

        return context


class ContentDeleteView(ContentView, DeleteView):

    template_name = "items/item_confirm_delete.html"

    def get_success_url(self):
        model_name = self.model.__name__
        if model_name == "Question":
            return self.object.item.get_absolute_url()
        elif model_name == "Item":
            return reverse("item_index")
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

        if context['model_name'] == "Question":
            context['item'] = self.object.item
        elif context['model_name'] == "Item":
            context['item'] = self.object

        return context


class ItemDetailView(DetailView):

    queryset = Item.objects.all()

    def get_context_data(self, **kwargs):
        context = super(ItemDetailView, self).get_context_data(**kwargs)
        if not self.request.POST:
#            initial = {'user': self.request.user}
            context['question_form'] = QuestionForm()   # (initial=initial)
        return context
