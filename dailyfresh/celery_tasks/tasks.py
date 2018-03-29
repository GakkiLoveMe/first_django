# coding = utf-8
from celery import Celery
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings
from django.core.mail import send_mail
from goods.models import GoodsCategory, IndexGoodsBanner, IndexPromotionBanner, IndexCategoryGoodsBanner
from django.shortcuts import render

# 创建应用
app = Celery('celery_tasks.tasks', broker='redis://127.0.0.1:6379/6')


@app.task
def send_active_email(id, email):
    """发送验证邮件"""

    # 用户信息加密
    serializer = Serializer(settings.SECRET_KEY, 60*60*2)
    value = serializer.dumps({'id': id})  # 返回byte
    value = value.decode()

    # 发送邮件
    msg = '<a href="http://127.0.0.1:8000/users/active/%s">邮箱验证</a>' % value
    send_mail("天天生鲜邮箱验证", "", settings.EMAIL_FROM, [email], html_message=msg)


@app.task
def generate_index():
    # 查询商品分类信息
    category_list = GoodsCategory.objects.all()

    # 首页中心轮换图片
    banner_list = IndexGoodsBanner.objects.all().order_by('index')

    # 推广图片
    promotion_list = IndexPromotionBanner.objects.all().order_by('index')[0:2]

    # 查询分类的推广产品
    for category in category_list:
        # 推广标题
        category.title_list = IndexCategoryGoodsBanner.objects.filter(category=category.id, display_type=0).order_by('index')[0:3]
        # 推广图片
        category.image_list = IndexCategoryGoodsBanner.objects.filter(category=category.id, display_type=1).order_by('index')[0:5]
    context = {
        'title': '首页',
        'category_list': category_list,
        'banner_list': banner_list,
        'promotion_list': promotion_list,
    }
    # 提取http响应体
    response = render(None, 'index.html', context)
    content = response.content.decode()

    # 写入静态文件
    with open(settings.GENERATE_HTML + 'index.html', 'w') as f:
        f.write(content)

