# -*- coding: utf-8 -*- 
"""
项目: sandboxMP
作者: 张强
创建时间: 2020-03-01 09:42
IDE: PyCharm
介绍:
"""
import json
from django.views.generic.base import TemplateView
from django.views.generic.base import View
from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from .mixin import LoginRequiredMixin
from .models import Structure
from .forms import StructureForm

User = get_user_model()


class Structure2UserView(LoginRequiredMixin, View):

    def get(self, request):
        if 'id' in request.GET and request.GET['id']:
            # 通过id获取需要绑定用户的组织架构实例
            structure = get_object_or_404(Structure, pk=int(request.GET['id']))
            # 通过外键的反向新查找(_set)，找到已经绑定到该组织架构的所有用户信息
            added_users = structure.userprofile_set.all()
            # 查找系统中所有用户信息，User = get_user_object()使用自定义用户模型都是通过这种模式
            all_user = User.objects.all()
            # 通过集合差集set().difference()，得出还未绑定的用户
            un_add_users = set(all_user).difference(added_users)
            # 将这些数据返回给前端，用来渲染数据，形成一个复选框，左边是未绑定用户，右边是已绑定用户
            ret = dict(structure=structure, added_users=added_users, un_add_users=list(un_add_users))
        return render(request, 'system/structure/structure_user.html', ret)

    def post(self, request):
        res = dict(result=False)
        id_list = None
        # 通过id获取structure实例
        structure = get_object_or_404(Structure, pk=int(request.POST['id']))
        # 获取需要绑定到structure实例的用户id
        if 'to' in request.POST and request.POST.getlist('to', []):
            id_list = map(int, request.POST.getlist('to', []))
        # 清空组织架构原有用户绑定信息
        structure.userprofile_set.clear()
        if id_list:
            # 绑定新用户数据
            for user in User.objects.filter(id__in=id_list):
                structure.userprofile_set.add(user)
        res['result'] = True
        return HttpResponse(json.dumps(res), content_type='application/json')


class StructureView(LoginRequiredMixin, TemplateView):
    template_name = "system/structure/structure.html"


class StructureCreateView(LoginRequiredMixin, View):

    def get(self, request):
        ret = dict(structure_all=Structure.objects.all())
        # 判断如果request.GET中包含id,则返回该条数据信息
        if 'id' in request.GET and request.GET['id']:
            structure = get_object_or_404(Structure, pk=request.GET['id'])
            ret['structure'] = structure
        return render(request, 'system/structure/structure_create.html', ret)

    def post(self, request):
        res = dict(result=False)
        # 如果request.POST中包含id则查找该实例，并传递给ModelForm的关键字参数instance,通过调用save()方法，将修改信息保存到该实例。
        if 'id' in request.POST and request.POST['id']:
            structure = get_object_or_404(Structure, pk=request.POST['id'])
            # 如果request.POST中ID不存在，则使用空的模型作为instance关键参数,调用save()方法,保存新建数据
            structure = Structure()
        structure_form = StructureForm(request.POST, instance=structure)
        if structure_form.is_valid():
            structure_form.save()
            res['result'] = True
        return HttpResponse(json.dumps(res), content_type='application/json')


class StructureListView(LoginRequiredMixin, View):

    def get(self, request):
        fields = ['id', 'name', 'type', 'parent__name']
        ret = dict(data=list(Structure.objects.values(*fields)))
        return HttpResponse(json.dumps(ret), content_type='application/json')


class StructureDeleteView(LoginRequiredMixin, View):

    def post(self, request):
        ret = dict(request=False)
        if 'id' in request.POST and request.POST['id']:
            id_list = map(int, request.POST['id'].split(','))
            Structure.objects.filter(id__in=id_list).delete()
            ret['result'] = True
        return HttpResponse(json.dumps(ret), content_type='application/json')
