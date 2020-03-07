# -*- coding: utf-8 -*- 
"""
项目: sandboxMP
作者: 张强
创建时间: 2020-03-06 09:21
IDE: PyCharm
介绍:
"""
import json
from django.views.generic.base import View
from django.views.generic import ListView
from django.shortcuts import render
from django.shortcuts import HttpResponse, Http404

from .mixin import LoginRequiredMixin
from .models import Menu
# from .forms import MenuForm
# from custom import SimpleInfoCreateView
from apps.custom import SandboxCreateView, SandboxUpdateView


class MenuCreateView(SandboxCreateView):
    model = Menu
    fields = '__all__'

    def get_context_data(self, **kwargs):
        kwargs['menu_all'] = Menu.objects.all()
        return super().get_context_data(**kwargs)


# class MenuCreateView(SandboxCreateView):
#     model = Menu
#     fields = '__all__'
#     extra_context = dict(menu_all=Menu.objects.all())


#
# class MenuCreateView(SimpleInfoCreateView):
#     model = Menu
#     fields = '__all__'
#     extra_context = dict(menu_all=Menu.objects.all())


# class MenuCreateView(LoginRequiredMixin, CreateView):
#     model = Menu
#     fields = '__all__'
#     success_url = '/system/rbac/menu/create'
#
#     def post(self, request, *args, **kwargs):
#         res = dict(result=False)
#         form = self.get_form()
#         if form.is_valid():
#             form.save()
#             res['result'] = True
#         return HttpResponse(json.dumps(res), content_type='application/json')

# class MenuCreateView(LoginRequiredMixin,View):
#
#     def get(self,request):
#         ret=dict(menu_all=Menu.objects.all())
#         return render(request,'system/rbac/menu_create.html',ret)
#
#     def post(self,request):
#         res =dict(result=False)
#         menu =Menu()
#         menu_form = MenuForm(request.POST,instance=menu)
#         if menu_form.is_valid():
#             menu_form.save()
#             res['result'] = True
#         return HttpResponse(json.dumps(res),content_type='application/json')

class MenuListView(LoginRequiredMixin, ListView):
    model = Menu
    context_object_name = 'menu_all'


class MenuUpdateView(SandboxUpdateView):
    model = Menu
    fields = '__all__'
    template_name_suffix = '_update'

    def get_context_data(self, **kwargs):
        kwargs['menu_all'] = Menu.objects.all()
        return super().get_context_data(**kwargs)

# class MenuUpdateView(SandboxUpdateView):
#     model = Menu
#     fields = '__all__'
#     template_name_suffix = '_update'
#     extra_context = dict(menu_all=Menu.objects.all())

# class MenuUpdateView(LoginRequiredMixin, UpdateView):
#     model = Menu
#     fields = '__all__'
#     template_name_suffix = '_update'
#     success_url = '/system/rbac/menu/'
#     extra_context = dict(menu_all=Menu.objects.all())
#
#     def get_object(self, queryset=None):
#
#         if queryset is None:
#             queryset = self.get_queryset()
#         if 'id' in self.request.GET and self.request.GET['id']:
#             queryset = queryset.filter(id=int(self.request.GET['id']))
#         elif 'id' in self.request.POST and self.request.POST['id']:
#             queryset = queryset.filter(id=int(self.request.POST['id']))
#         else:
#             raise AttributeError("Generic detail view %s must be called with id."
#                                  % self.__class__.__name__)
#         try:
#             obj = queryset.get()
#         except queryset.model.DoesNotExist:
#             raise Http404(
#                 "No %(verbose_name found matching the query" % {'verbose_name': queryset.model._meta.verbose_name})
#         return obj
#
#     def post(self, request, *args, **kwargs):
#
#         self.object = self.get_object()
#         res = dict(result=False)
#         form = self.get_form()
#         if form.is_valid():
#             form.save()
#             res['result'] = True
#         return HttpResponse(json.dumps(res), content_type='application/json')
