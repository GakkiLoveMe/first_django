from django.shortcuts import render, redirect
from django.views.generic import View
from django.http import HttpResponse, JsonResponse
import re
from .models import User, Address
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired
from django.conf import settings
from django.core.mail import send_mail
from celery_tasks.tasks import send_active_email
from django.contrib.auth import authenticate, login

# Create your views here.

# def register(request):
#     """用户注册模块"""
#     if request.method == 'GET':
#         return render(request, 'register.html')
#     elif request.method == 'POST':
#         return HttpResponse('处理post请求')


class RegisterView(View):
    """类视图:用户注册"""

    def get(self, request):
        """处理GET请求"""
        return render(request, 'register.html',{'title': '注册'})

    def post(self, request):
        """处理POST请求"""

        # 获取请求信息
        name = request.POST.get('user_name')
        pwd = request.POST.get('pwd')
        cpwd = request.POST.get('cpwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        # 构造用户输入上下文
        context = {
            'name': name,
            'pwd': pwd,
            'cpwd': cpwd,
            'email': email,
            'err_msg': '',
            'title': '注册',
        }

    # 1,对信息进行校验

        # 是否勾选协议
        if not allow:
            context['err_msg'] = '请同意协议!'
            return render(request, 'register.html', context)

        # 是否填写完整
        if not all([name, pwd, cpwd, email]):
            context['err_msg'] = '信息请填写完整!'
            return render(request, 'register.html', context)

        # 判断密码是否一致
        if pwd != cpwd:
            context['err_msg'] = '密码不一致'
            return render(request, 'register.html', context)

        # 判断邮箱是否正确
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            context['err_msg'] = '请输入正确的邮箱!'
            return render(request, 'register.html', context)

        # 判断邮箱是否存在
        if User.objects.filter(email=email).count() > 0:
            context['err_msg'] = '邮箱已经存在'
            return render(request, 'register.html', context)

        # 判断用户名是否存在
        if User.objects.filter(username=name).count() > 0:
            context['err_msg'] = '用户名已经存在'
            return render(request, 'register.html', context)

    # 2,校验通过,则储存用户对象
        user = User.objects.create_user(username=name, password=pwd, email=email)
        # 默认不激活账户
        user.is_active = False
        user.save()

    # 3,给用户发送激活邮件

        # 用户信息加密
        # serializer = Serializer(settings.SECRET_KEY, 60*60*2)
        # value = serializer.dumps({'id': user.id})  # 返回byte
        # value = value.decode()

        # 发送邮件
        # msg = '<a href="http://127.0.0.1:8000/users/active/%s">邮箱验证</a>' % value
        # send_mail("天天生鲜邮箱验证", "", settings.EMAIL_FROM, [email],
        #           html_message=msg)

        # celery 发送异步邮件
        send_active_email.delay(email, user.id)

    # 4,通知用户激活
        return HttpResponse('邮件已发送,为了不影响您的使用,请在两个小时内确认邮件!')


def active(request, value):
    """用于激活确认"""
    # 接收用户确认链接
    serializer = Serializer(settings.SECRET_KEY)
    try:
        dict = serializer.loads(value)
        uid = dict.get('id')

        # 激活邮箱
        user = User.objects.get(id=uid)
        user.is_active = True
        user.save()

        # 转向登陆页面
        return redirect('/users/login')
    except SignatureExpired as e:
        return HttpResponse('对不起,激活链接已过期!')


def exists(request):
    """判断邮箱或者用户名是否存在"""

    # 1,判断用户名
    user_name = request.GET.get('user_name')
    if user_name is not None:
        result = User.objects.filter(username=user_name).count()
        return JsonResponse({"result": result})

    # 2,判断邮箱
    user_email = request.GET.get('user_email')
    if user_email:
        result = User.objects.filter(email=user_email).count()
        return JsonResponse({"result": result})


class LoginView(View):
    """类视图: 用户登陆"""

    # 1,处理GET请求
    def get(self, request):
        user_name = request.GET.get('user_name', '')  # 设置默认值为空，否则开始传值为none
        return render(request, 'login.html',{'title': '登陆', 'user_name': user_name})

    # ２,处理POST请求
    def post(self, request):
        user_name = request.POST.get('username')
        user_pwd = request.POST.get('pwd')
        remember = request.POST.get('remember')

        # 用户信息存贮
        context = {
            'user_name': user_name,
            'user_pwd': user_pwd,
            'err_msg': '',
            'title': '登陆',
        }
    # 3,登陆信息验证

        # 信息是否填写完整
        if not all([user_name, user_pwd]):
            context['err_msg'] = '请填入完整信息'
            # print(1)
            return render(request, 'login.html', context)

        # 验证用户名和密码是否存在
        user = authenticate(username=user_name, password=user_pwd)
        if user is None:
            context['err_msg'] = '用户名或密码错误'
            # print(2)
            return render(request, 'login.html', context)

        # 验证用户是否激活
        if user.is_active is False:
            context['err_msg'] = '请到您的邮箱激活账户'
            # print(3)
            return render(request, 'login.html', context)

        # 记录状态,记录session
        login(request, user)

        # 是否记住用户名
        response = redirect('/users/index')
        if remember is not None:
            # print(4)
            response.set_cookie('user_name', user_name, expires=60*60*24*7)
        else:
            response.delete_cookie('user_name')

    # 4,验证通过转向主页
        return response


def index(request):
    return render(request, 'index.html')

