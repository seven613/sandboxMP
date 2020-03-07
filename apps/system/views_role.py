# -*- coding: utf-8 -*- 
"""
项目: sandboxMP
作者: 张强
创建时间: 2020-03-07 08:28
IDE: PyCharm
介绍:
"""
import json

from django.views.generic import TemplateView
from django.views.generic.base import View
from django.shortcuts import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.shortcuts import render

User = get_user_model()

from .mixin import LoginRequiredMixin
from .models import Role,Menu
from custom import SandboxCreateView, SandboxUpdateView


class RoleView(LoginRequiredMixin, TemplateView):
    template_name = 'system/role.html'


class RoleCreateView(SandboxCreateView):
    model = Role
    fields = '__all__'


class RoleListView(LoginRequiredMixin, View):

    def get(self, request):
        fields = ['id', 'name', 'desc']
        ret = dict(data=list(Role.objects.values(*fields)))
        return HttpResponse(json.dumps(ret), content_type='application/json')


class RoleUpdateView(SandboxUpdateView):
    model = Role
    fields = '__all__'
    template_name_suffix = '_update'


class RoleDeleteView(LoginRequiredMixin, View):

    def post(self, request):
        ret = dict(restult=False)
        if 'id' in request.POST and request.POST['id']:
            id_list = map(int, request.POST['id'].split(','))
            Role.objects.filter(id__in=id_list).delete()
            ret['restult'] = True
        return HttpResponse(json.dumps(ret), content_type='application/json')


class Role2UserView(LoginRequiredMixin, View):
    """
    角色关联
    """

    def get(self, request):
        if 'id' in request.GET and request.GET['id']:
            # 通过id获取需要绑定用户的角色组实例
            role = get_object_or_404(Role, pk=int(request.GET.get('id')))
            # 通过外键的反向查找(_set),找到已经绑定到该角色组的所有用户信息
            added_users = role.userprofile_set.all()
            # 查找系统中所有用户
            all_users = Role.objects.all()
            # 通过集合获取差集set().difference()，得出还未绑定的用户
            un_add_users = set(all_users).difference(added_users)
            # 将这些数据返回给前端，用来渲染数据，形成一个复选框，左边是未绑定用户，右边是已经绑定用户
            ret = dict(role=role, added_users=added_users, un_add_users=list(un_add_users))
        return render(request, 'system/role_role2user.html', ret)

    def post(self, request):
        res = dict(result=False)
        id_list = None
        role = get_object_or_404(Role, pk=int(request.POST.get['id']))
        if 'to' in request.POST and request.POST['to']:
            id_list = map(int, request.POST.getlist('to', []))
        role.userprofile_set.clear()
        if id_list:
            for user in User.objects.filter(id__in=id_list):
                role.userprofile_set.add(user)
        res['result']=True
        return HttpResponse(json.dumps(res),content_type='application/json')

class Role2MenuView(LoginRequiredMixin,View):
    """
    角色 绑定菜单
    """
    def get(self,request):
        if 'id' in request.GET and request.GET['id']:
            role =get_object_or_404(Role,pk=request.GET['id'])
            ret=dict(role=role)
            return render(request,'system/role_role2menu.html',ret)

    def post(self,request):
        res =dict(result=False)
        role = get_object_or_404(Role,pk=request.POST['id'])
        #清除原有的权限信息（如果前端点了生成干你，并没有选中菜单，则改角色组权限将被清空）
        tree = json.loads(self.request.POST['tree'])
        role.permissions.clear()
        #遍历前端传来的绑定菜单，根据id查找菜单实例，然后将菜单添加到当前角色组
        for menu in tree:
            if menu['checked'] is True:
                menu_checked = get_object_or_404(Menu,pk=menu['id'])
                role.permissions.add(menu_checked)
        res['result']=True
        return HttpResponse(json.dumps(res),content_type='application/json')

class Role2MeunListView(LoginRequiredMixin,View):
     """
        zTree在生成带单树装结构时，会通过该接口获取菜单列表数据
     """
     def get(self,request):
         fields=['id','name','parent']
         if 'id' in request.GET and request.GET['id']:
             role = Role.objects.get(id=request.GET.get('id'))
             role_menus = role.permissions.values(*fields)
             ret = dict(data=list(role_menus))
         else:
             menus = Menu.objects.all()
             ret = dict(data=list(menus.values(*fields)))
         return HttpResponse(json.dumps(ret),content_type='application/json')
