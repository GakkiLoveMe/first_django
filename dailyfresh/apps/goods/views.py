from django.shortcuts import render
from .models import GoodsCategory, Goods, GoodsSKU, GoodsImage, IndexGoodsBanner, IndexCategoryGoodsBanner, IndexPromotionBanner
from django.core.cache import cache  # 设置缓存API
from django.http import Http404
from django.core.paginator import Paginator, Page  # 分页功能
from django_redis import get_redis_connection
from haystack.generic_views import SearchView  # haystack自定义视图
from utils.page_list import get_page_list
import json

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
    # 读取购物车数量
    total_count = get_total_count(request)
    context['total_count'] = total_count

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

    # 构造上下文
    context = {
        'title': '商品详情',
        'sku': sku,
        'category': category,
        'new_list': new_list,
        'other_list': other_list,
    }

    # 保存用户最近浏览
    if request.user.is_authenticated():
        key = 'history%d' % request.user.id
        redis_client = get_redis_connection()
        # 删除重复的商品
        redis_client.lrem(key, 0, sku.id)
        # 添加商品
        redis_client.lpush(key, sku.id)
        # 浏览商品上限,删除多余
        if redis_client.llen(key) > 5:
            redis_client.rpop(key)

    # 读取购物车数量
    context['total_count'] = get_total_count(request)

    return render(request, 'detail.html', context)


def list(request, category_id):
    """商品列表页"""
    try:
        # 当前分类对象
        category_now = GoodsCategory.objects.get(id=category_id)
    except:
        raise Http404()

    # 获取页码
    index_id = int(request.GET.get('pindex', '1'))

    # 获取排序
    order_id = int(request.GET.get('order', 1))

    # 分类信息
    category_list = GoodsCategory.objects.all()

    # 当前分类新品
    new_list = category_now.goodssku_set.all().order_by('-id')[0:2]

    # 进行排序
    if order_id == 2:
        order_by = 'price'
    elif order_id == 3:
        order_by = '-price'
    elif order_id == 4:
        order_by = 'sales'
    else:
        order_by = '-id'

    # 分类所有商品
    slist = category_now.goodssku_set.all().order_by(order_by)
    paginator = Paginator(slist, 1)
    total = paginator.num_pages

    # 进行页码有效性判断
    if index_id <= 1:
        index_id = 1
    if index_id >= total:
        index_id = total

    # 根据请求返回不同分页
    page = paginator.page(index_id)

    # 获取页码列表
    page_list = get_page_list(total, index_id)

    # 构造上下文
    context = {
        "title": '商品列表',
        'category_now': category_now,
        'category_list': category_list,
        'new_list': new_list,
        'page': page,
        'page_list': page_list,
        'order_id': order_id,
        }

    # 读取购物车数量
    context['total_count'] = get_total_count(request)

    return render(request, 'list.html', context)


class MySearchView(SearchView):
    """My custom search view."""
    # index_id = 0

    def __init__(self, *args, **kwargs):
        super(MySearchView, self).__init__(*args, **kwargs)

        # 分类信息
        self.category_list = GoodsCategory.objects.all()

    def get(self, request, *args, **kwargs):

        get_request = super(MySearchView, self).get(request, *args, **kwargs)

        # 获取页码
        # self.index_id = int(request.GET.get('pindex', 1))
        self.request = request

        return get_request

    def get_context_data(self, *args, **kwargs):
        """重构上下文"""
        # self.get(request)
        context = super(MySearchView, self).get_context_data(*args, **kwargs)
        context['title'] = '商品搜索'
        context['category_list'] = self.category_list

        # 获取总页面总数
        total = context['paginator'].num_pages
        index_id = context['page_obj'].number

        context['page_list'] = get_page_list(total, index_id)

        # do something
        # 返回当前请求的分页
        # context['page_obj'] = context['paginator'].page(index_id)
        # 读取购物车数量
        context['total_count'] = get_total_count(self.request)

        return context


def get_total_count(request):
    """获取所有商品的数量"""
    total_count = 0
    if request.user.is_authenticated():
        redis_cli = get_redis_connection()
        for count in redis_cli.hvals('cart%d' % request.user.id):
            total_count += int(count)
    else:
        cart_str = request.COOKIES.get('cart')
        if cart_str:
            cart_list = json.loads(cart_str)
            for k, v in cart_list.items():
                total_count += v

    return total_count

