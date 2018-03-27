from django.shortcuts import render
from .models import GoodsCategory, Goods, GoodsSKU, GoodsImage, IndexGoodsBanner, IndexCategoryGoodsBanner, IndexPromotionBanner

# Create your views here.


def index(request):
    """显示主页"""
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
    return render(request, 'index.html', context)
