from django.db import models


class BaseModel(models.Model):
    """创建基类"""
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')  # 创建时间
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')  # 更新时间
    is_delete = models.BooleanField(default=False, verbose_name='逻辑删除')  # 逻辑删除

    class Meta:
        """修改默认,不把基类当做模型类来创建表"""
        abstract = True
