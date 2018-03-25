# coding = utf-8
from celery import Celery
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings
from django.core.mail import send_mail

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
