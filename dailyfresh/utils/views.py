"""类试图添加装饰器"""
from django.views.generic import View
from django.contrib.auth.decorators import login_required


class LoginRequiredView(View):
    """直接定义一个类继承View"""
    @classmethod
    def as_view(cls, **initkwargs):
        func = super().as_view(**initkwargs)
        return login_required(func)


class LoginRequiredViewMixin(object):
    """多继承方法"""
    @classmethod
    def as_view(cls, **initkwargs):
        func = super().as_view(**initkwargs)
        return login_required(func)