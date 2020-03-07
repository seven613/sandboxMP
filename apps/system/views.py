from django.shortcuts import render
from django.views.generic.base import View
from django.views.generic.base import TemplateView

from .mixin import LoginRequiredMixin


class SystemView(LoginRequiredMixin, TemplateView):

    template_name = 'system/system_index.html'
#
# class SystemView(LoginRequiredMixin, View):
#
#     def get(self, request):
#         return render(request, 'system/system_index.html')