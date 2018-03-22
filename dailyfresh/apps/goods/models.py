from django.db import models
from utils.models import BaseModel

# Create your models here.


class GoodsCategory(BaseModel):
    """商品分类表"""
    name = models.CharField(max_length=20, verbose_name='名称')
    logo = models.CharField(max_length=100, verbose_name='图标')
    image = models.ImageField(upload_to='category', verbose_name='图片')

    class Meta:
        db_table = "df_goods_category"
        verbose_name = "商品分类"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Goods(BaseModel):
    """商品SPU表"""
    name = models.CharField(max_length=100, verbose_name='名称')
    # TODO 详细介绍

    class Meta:
        db_table = "df_goods"
        verbose_name = "商品"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class GoodsSKU(BaseModel):
    """商品SKU表"""
    name = models.CharField(max_length=100, verbose_name='名称')
    title = models.CharField(max_length=200, verbose_name='简介')
    unit = models.CharField(max_length=10, verbose_name='销售单位')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='售价')
    stock = models.IntegerField(default=0, verbose_name='库存')
    sales = models.IntegerField(default=0, verbose_name='销量')
    default_image = models.ImageField(upload_to='goods', verbose_name='默认图片')
    status = models.BooleanField(default=False, verbose_name='是否上线')
    category = models.ForeignKey(GoodsCategory, verbose_name='分类信息')
    goods = models.ForeignKey(Goods, verbose_name='种类商品')

    class Meta:
        db_table = 'df_goods_sku'
        verbose_name = '商品SKU'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class GoodsImage(BaseModel):
    """商品图片"""
    image = models.ImageField(upload_to='goods', verbose_name="商品图片")
    sku = models.ForeignKey(GoodsSKU, verbose_name="商品SKU")

    class Meta:
        db_table = 'df_goods_image'
        verbose_name = "商品图片"
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.sku)


class IndexGoodsBanner(BaseModel):
    """主页轮换图片"""
    sku = models.ForeignKey(GoodsSKU, verbose_name='商品SKU')
    image = models.ImageField(upload_to='banner', verbose_name='图片')
    index = models.SmallIntegerField(default=0, verbose_name='顺序')

    class Meta:
        db_table = 'df_index_goods'
        verbose_name = '主页轮播图片'
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.sku)
    

