from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Home View."""
    template_name = 'index.html'
    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        return context



