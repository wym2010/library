from django.views import generic
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Book, Author


class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'hs_library/index.html'
    context_object_name = 'book_list'
    login_url = 'hs_library:login'


    def get_queryset(self):
        return Book.objects.order_by('-shelf_time')[:5]

#TODO
class DetailView(LoginRequiredMixin, generic.DetailView):
    model = Book
    template_name = 'hs_library/detail.html'
    login_url = 'hs_library:login'
    redirect_field_name = 'detail'


class ResultsView(generic.DetailView):
    model = Book
    template_name = 'hs_library/results.html'


class MustLoginFormView(LoginRequiredMixin, generic.FormView):
    pass


class LoginOutView(LoginView, LogoutView):
    pass

