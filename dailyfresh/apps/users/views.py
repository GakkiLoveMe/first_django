from django.shortcuts import render, redirect
from django.views.generic import View  # 创建类试图
from django.http import HttpResponse, JsonResponse
import re
from .models import User, Address, AreaInfo
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired  # 签名加密
from django.conf import settings
from django.core.mail import send_mail  # django 邮件发送模块
from celery_tasks.tasks import send_active_email
from django.contrib.auth import authenticate, login, logout  # 验证，登陆，登出
from django.contrib.auth.decorators import login_required  # 验证登陆装饰器
from django_redis import get_redis_connection  # django链接redis
from goods.models import GoodsSKU

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
        user = User.objects.create_user(name, email, pwd)
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
        send_active_email.delay(user.id, user.email)

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
        response = redirect('/users/info')
        if remember is not None:
            # print(4)
            response.set_cookie('user_name', user_name, expires=60*60*24*7)
        else:
            response.delete_cookie('user_name')

    # 4,验证通过转向主页
        return response


def logout_user(request):
    """退出登陆"""
    logout(request)
    return redirect('/users/login')


@login_required
def info(request):
    """用户中心"""
    # 从redis读取浏览数据
    client = get_redis_connection()
    history_list = client.lrange("history%s" % request.user.id, 0, -1)
    history_list2 = list()
    if history_list:
        for gid in history_list:
            history_list2.append(GoodsSKU.objects.filter(pk=gid))
    # 查询默认收货地址,显示信息
    addr = request.user.address_set.all().filter(isDefault=1)
    if addr:
        addr = addr[0]
    else:
        addr = ''

    context = {
        'title': '个人信息',
        'addr': addr,
        'history_list2': history_list2,
    }
    return render(request, 'user_center_info.html', context)


@login_required
def order(request):
    """用户订单页"""
    # 构造上下文
    context = {
        'title': '全部订单',
    }
    return render(request, 'user_center_order.html', context)


class SiteView(View):
    """显示和添加用户地址"""
    def get(self, request):
        # 处理get请求
        addr_list = Address.objects.filter(user=request.user)
        context = {
            'title': '收货地址',
            'addr_list': addr_list,
        }
        return render(request, 'user_center_site.html', context)

    def post(self, request):
        # 处理post请求
        receiver = request.POST.get('receiver')
        phone = request.POST.get('phone')
        detail_addr = request.POST.get('addr')
        code = request.POST.get('code')
        province = request.POST.get('province')
        city = request.POST.get('city')
        district = request.POST.get('district')
        default = request.POST.get('default')
        user = request.user

        # 构造上下文
        context = {
            'title': '收货地址',
            'err_msg': '',
        }

        # 判断信息是否完整
        if not all([receiver, phone, detail_addr, code, province, city, district]):
            context['err_msg'] = '请把填写信息完整'
            return render(request, 'user_center_site.html', context)

        # 保存用户地址信息
        addr = Address()
        addr.user = user
        addr.receiver_name = receiver
        addr.receiver_mobile = phone
        addr.zip_code = code
        addr.province_id = province
        addr.city_id = city
        addr.detail_addr = detail_addr
        addr.district_id = district

        # 判断是否为默认地址
        if default is not None:
            addr.isDefault = True

        addr.save()
        return redirect('/users/site')


def area(request):
    """接收ajax请求显示地区"""
    pid = request.GET.get('pid')
    if pid is None:
        # 显示省市
        slist = AreaInfo.objects.filter(aParent__isnull=True)
    else:
        slist = AreaInfo.objects.filter(aParent_id=pid)
    slist2 = list()
    # 重新组织数据格式
    for s in slist:
        slist2.append({'id': s.id, 'title': s.title})
    return JsonResponse({'slist2': slist2})
