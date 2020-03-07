# -*- coding: utf-8 -*- 
"""
项目: sandboxMP
作者: 张强
创建时间: 2020-03-01 09:35
IDE: PyCharm
介绍:
"""

from django.contrib.auth.decorators import login_required


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **init_kwargs):
        view = super(LoginRequiredMixin, cls).as_view(**init_kwargs)
        return login_required(view)