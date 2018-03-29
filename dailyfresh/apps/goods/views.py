from django.shortcuts import render
from .models import GoodsCategory, Goods, GoodsSKU, GoodsImage, IndexGoodsBanner, IndexCategoryGoodsBanner, IndexPromotionBanner
from django.core.cache import cache  # 设置缓存API
from django.http import Http404
from django.core.paginator import Paginator, Page  # 分页功能

# Create your views here.


def index(request):
    """显示主页"""
    # 先优先读取缓存
    context = cache.get('index')

    # 判断是否存在缓存
    if context is None:
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

        # 设置缓存
        cache.set('index', context, 3600)

    return render(request, 'index.html', context)


def detail(request, sku_id):
    """商品详情页"""
    try:
        # 查询商品SKU信息
        sku = GoodsSKU.objects.get(pk=sku_id)
    except:
        raise Http404()

    # 商品分类
    category = GoodsCategory.objects.all()

    # 新品推荐
    new_list = sku.category.goodssku_set.all().order_by('-id')[0:2]

    # 其他规格产品
    other_list = sku.goods.goodssku_set.all()

    context = {
        'title': '商品详情',
        'sku': sku,
        'category': category,
        'new_list': new_list,
        'other_list': other_list,
    }
    return render(request, 'detail.html', context)
    pass


def list(request, category_id):
    """商品列表页"""
    # 当前分类对象
    category_now = GoodsCategory.objects.get(id=category_id)

    # 分类信息
    category_list = GoodsCategory.objects.all()

    # 当前分类新品
    new_list = category_now.goodssku_set.all().order_by('-id')[0:2]

    # 分类所有商品
    category_all = category_now.goodssku_set.all()
    page

    # 构造上下文
    context = {
        "title": '商品列表',
        'category_now': category_now,
        'category_list': category_list,
        'new_list': new_list,
    }
    return render(request, 'list.html', context)