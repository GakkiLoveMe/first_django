from django.db import models
from django.contrib.auth.models import AbstractUser
from utils.models import BaseModel

# Create your models here.


class User(BaseModel, AbstractUser):
    """创建用户类,继承于django提供的用户类和基类"""

    class Meta:
        db_table = "df_users"


class Address(BaseModel):
    """用户地址"""
    user = models.ForeignKey(User, verbose_name='所属用户')
    receiver_name = models.CharField(max_length=20, verbose_name='收件人')
    receiver_mobile = models.CharField(max_length=11, verbose_name='手机号')
    detail_addr = models.CharField(max_length=256, verbose_name='详细地址')
    zip_code = models.CharField(max_length=6, verbose_name='邮政编码')
    province = models.ForeignKey('AreaInfo', related_name='province', default='')
    city = models.ForeignKey('AreaInfo', related_name='city', default='')
    district = models.ForeignKey('AreaInfo', related_name='district', default='')
    isDefault = models.BooleanField(default=0)

    class Meta:
        db_table = "df_address"


class AreaInfo(models.Model):
    """地区模型类"""
    title = models.CharField(max_length=20)
    aParent = models.ForeignKey('self', null=True, blank=True)

    class Meta:
        db_table = 'df_areas'

