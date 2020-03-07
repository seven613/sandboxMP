# -*- coding: utf-8 -*- 
"""
项目: sandboxMP
作者: 张强
创建时间: 2020-03-07 15:18
IDE: PyCharm
介绍:
"""
import re

from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.shortcuts import render


class MenuCollection(MiddlewareMixin):

    def get_user(self, request):
        return request.user

    # 注释1： 从request中获取用户信息，获取用户角色组绑定的菜单信息，其中distinct()
    # 是用来去重，因为用户可继承多个角色组权限，有可能多个角色组都绑定了同一个菜单。后面的列表推到式是用来排除空角色组的菜单信息。如果用户没有登陆，则返回None，最终获取的数据格式是一个包含菜单字典的列表：
    # [{'permissionsid': 1, 'permissionsname': '系统管理', 'permissionsurl': '/system/', 'permissionsicon': None,
    #   'permissionscode': 'SYSTEM', 'permissionsparent': None}, ...]。
    def get_menu_from_role(self, request, user=None):
        if user is None:
            user = self.get_user(request)
        try:
            menus = user.roles.values(
                'permissions__id',
                'permissions__name',
                'permissions__url',
                'permissions__icon',
                'permissions__code',
                'permissions__parent'
            ).distinct()
            return [menu for menu in menus if menu['permissions__id'] is not None]
        except AttributeError:
            return None
    #注释2： 从1中获取的列表中提取出url生成一个新的列表，这个列表中是从用户角色中获取的所有URL，用来比对用户访问的URL是否在这个列表中。获取的内容如下：
#['/system/', None, '/system/basic/structure/', '/system/basic/structure/list', '/system/basic/structure/create', '/system/basic/structure/delete', ...]
    def get_permission_url(self, request):
        role_menus = self.get_menu_from_role(request)
        if role_menus is not None:
            permission_url_list = [menu['permission__url'] for menu in role_menus]
            return permission_url_list
    #注释3： 对1中获取的列表重新组合，替换原有键的名称，换成和数据库中对应的字段名称，同时添加了两个新的键值对: status用来标识头部一级菜单的选中状态，默认False；sub_menu默认是一个列表，用来存放下级菜单数据。
    def get_permission_menu(self, request):
        permission_menu_list = []
        role_menus = self.get_menu_from_role(request)
        if role_menus is not None:
            for item in role_menus:
                menu = {
                    'id': item['permission__id'],
                    'name': item['permission__name'],
                    'url': item['permission__url'],
                    'icon': item['permission__icon'],
                    'code': item['permission__code'],
                    'parent': item['permission__parent'],
                    'status': False,
                    'sub_menu': [],
                }
                permission_menu_list.append(menu)
            return permission_menu_list

    # 注释4： 获取头部导航和侧边栏导航数据，更具层级进行组合，最后返回数据格式如下：
    # ([{'id': 1, 'name': '系统管理', 'url': '/system/', 'icon': None, 'code': 'SYSTEM', 'parent': None, 'status': True, 'sub_menu': [{'id': 2, 'name': '基础设置', 'url': None, 'icon': 'fa fa-gg', 'code': 'SYSTEM-BASIC', 'parent': 1, 'status': False, 'sub_menu': [{'id': 3, 'name': '组织架构', 'url': '/system/basic/structure/', 'icon': None, 'code': 'SYSTEM-BASIC-STRUCTURE', 'parent': 2, 'status': False, 'sub_menu': [{'id': 4, 'name': '组织架构：列表', 'url': '/system/basic/structure/list', 'icon': None, 'code': 'SYSTEM-BASIC-STRUCTURE-LIST', 'parent': 3, 'status': False, 'sub_menu': []}, {'id': 5, 'name': '组织架构：创建', 'url': '/system/basic/structure/create', 'icon': None, 'code': 'SYSTEM-BASIC-STRUCTURE-CREATE', 'parent': 3, 'status': False, 'sub_menu': []}, {'id': 6, 'name': '组织架构：删除', 'url': '/system/basic/structure/delete', 'icon': None, 'code': 'SYSTEM-BASIC-STRUCTURE-DELETE', 'parent': 3, 'status': False, 'sub_menu': []}, {'id': 7, 'name': '组织架构：关联用户', 'url': '/system/basic/structure/add_user', 'icon': None, 'code': 'SYSTEM-BASIC-STRUCTURE-ADD_USER', 'parent': 3, 'status': False, 'sub_menu': []}]}, }])
    def get_top_reveal_menu(self, request):
        top_menu = []
        permission_menu_dict = {}
        request_url = request.path_info
        permission_menu_list = self.get_permission_menu(request)
        if permission_menu_list is not None:
            for menu in permission_menu_list:

                url = menu['url']
                if url and re.match(url, request_url):
                    menu['status'] = True
                if menu['parent'] is None:
                    top_menu.insert(0, menu)
                permission_menu_dict[menu['id']] = menu

        menu_data = []
        for i in permission_menu_dict:
            if permission_menu_dict[i]['parent']:
                pid = permission_menu_dict[i]['parent']
                parent_menu = permission_menu_dict[pid]
                parent_menu['sub_menu'].append(permission_menu_dict[i])
            else:
                menu_data.append(permission_menu_dict[i])
        if [menu['sub_menu'] for menu in menu_data if menu['url'] in request_url]:
            reveal_menu = [menu['sub_menu'] for menu in menu_data if menu['url'] in request_url[0]]
        else:
            reveal_menu = None
        return top_menu, reveal_menu

    # 注释5： process_request()
    # 是在将request请求传递给view前执行，所有在这里我们把整理组合好的菜单数据写入request。
    def process_request(self, request):

        if self.get_top_reveal_menu(request):
            request.top_menu, request.reveal_menu = self.get_top_reveal_menu(request)
            request.permission_url_list = self.get_permission_url(request)

class RbacMiddleware(MiddlewareMixin):

    def process_request(self,request):
        if hasattr(request,'permission_url_list'):
            request_url = request.path_info
            permission_url =request.permission_url_list
            for url in settings.SAFE_URL:
                if re.match(url,request_url):
                    return None
            if request_url in permission_url:
                return None
            else:
                return render(request,'page404.html')