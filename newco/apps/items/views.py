from django.views.generic import DetailView, CreateView
from django.views.generic import UpdateView, DeleteView
from django.core.urlresolvers import reverse
from django.http import Http404

from items.models import Item
from items.forms import ItemForm


class ItemCreateView(CreateView):

    model = Item
    form_class = ItemForm

    def form_valid(self, form):
        self.object = form.save(commit=False)

        if self.request.user.is_authenticated():
            self.object.user = self.request.user

        return super(ItemCreateView, self).form_valid(form)


class ItemUpdateView(UpdateView):

    model = Item
    form_class = ItemForm

    def get_object(self, queryset=None):
        obj = Item.objects.get(pk=self.kwargs['id'])
        return obj


class ItemDeleteView(DeleteView):

    context_object_name = "item"
    queryset = Item.objects.all()

    def get_success_url(self):
        return reverse("item_index")

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(ItemDeleteView, self).get_object()
        if obj.user and not obj.user == self.request.user:
            raise Http404
        return obj


class ItemDetailView(DetailView):

    context_object_name = "item"
    queryset = Item.objects.all()

    def get_object(self):
        # Call the superclass
        object = super(ItemDetailView, self).get_object()
        # Return the object
        return object
