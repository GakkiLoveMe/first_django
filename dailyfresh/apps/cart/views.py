from django.shortcuts import render
from django.http import JsonResponse, Http404
from django_redis import get_redis_connection
import json  # 用于字典与字符串之间转换
from goods.models import GoodsSKU

# Create your views here.


def cart(request):
    """购物车"""
    # 购物车列表
    sku_list = []

    # 用户登陆后,从redis读取数据
    if request.user.is_authenticated():
        # 连接数据库
        redis_cli = get_redis_connection()
        key = 'cart%d' % request.user.id
        id_list = redis_cli.hkeys(key)
        for gid in id_list:
            sku = GoodsSKU.objects.get(pk=gid)
            sku.cart_count = int(redis_cli.hget(key, gid))  # 添加一个属性,把数量传递过去
            sku_list.append(sku)
    else:
        # 没有登陆从cookies读取
        cart_str = request.COOKIES.get('cart')
        if cart_str:
            cart_list = json.loads(cart_str)
            for k, v in cart_list.items():
                sku = GoodsSKU.objects.get(pk=k)
                sku.cart_count = v
                sku_list.append(sku)

    context = {
        'title': '购物车',
        'sku_list': sku_list,
    }
    return render(request, 'cart.html', context)


def add(request):
    """购物车添加功能"""
    # Post请求验证
    if request.method != 'POST':
        return Http404()

    # 接收请求,获取sku和数量
    dict = request.POST
    sku_id = dict.get("sku_id", 0)
    count = int(dict.get("count", 0))

    # 后端进行数据验证
    if GoodsSKU.objects.filter(pk=sku_id).count() <= 0:
        return JsonResponse({'status': 2})
    if count <= 0:
        return JsonResponse({'status': 3})

    # 判断用户是否登陆
    if request.user.is_authenticated():
        # 读取cookies信息存储到redis中
        # cart_str = request.GET.get('cart')
        # cart_dict = json.loads(cart_str)
        # 链接数据库
        redis_cli = get_redis_connection()
        key = 'cart%d' % request.user.id

        # 存储字典
        # for k, v in cart_dict.items():
        # 判断是否存在相同商品
        if redis_cli.hexists(key, sku_id):
            count0 = int(redis_cli.hget(key, sku_id))
            count1 = count + count0
            if count1 > 5:
                count1 = 5
            redis_cli.hset(key, sku_id, count1)
        else:
            redis_cli.hset(key, sku_id, count)

        # 获取购物车数量
        total_num = 0
        for num in redis_cli.hvals(key):
            total_num += int(num)

        return JsonResponse({'status': 1, 'count': total_num})

    else:
        # 未登录的情况下保存在cookie中

        # 读取已有cookie数据
        cart_str = request.COOKIES.get('cart')
        if cart_str:
            cart_dict = json.loads(cart_str)
        else:
            cart_dict = {}

        # 获取购物车数量,如果相同,相加
        if sku_id in cart_dict:
            count = cart_dict[sku_id] + count
            # 购物数量限制
            if count > 5:
                count = 5
        # 重构cookies
        cart_dict[sku_id] = count

        # 获取购物车的物品数量
        total_num = 0
        for k, v in cart_dict.items():
            total_num += v

        # 设置新的cookie数据
        cart_str = json.dumps(cart_dict)  # 进行字符串转换
        response = JsonResponse({'status': 1, 'count': total_num})
        response.set_cookie('cart', cart_str, expires=60*60*24*14)

        return response


def edit(request):
    """编辑购物车"""
    # 接收请求
    if request.method != 'POST':
        return Http404()
    # 接收数据
    sku_id = request.POST.get('sku_id')
    count = int(request.POST.get('count'))

    # 后端有效性判断
    if GoodsSKU.objects.filter(pk=sku_id).count() <= 0:
        return JsonResponse({'status': 2})
    if count <= 0:
        count = 1
    elif count >= 5:
        count = 5
    # 构造返回体
    response = JsonResponse({'status': 1})

    # 数据处理
    if request.user.is_authenticated():
        # redis中处理
        redis_cli = get_redis_connection()
        redis_cli.hset('cart%d' % request.user.id, sku_id, count)
        pass
    else:
        # cookies中处理
        cart_str = request.COOKIES.get('cart')
        if cart_str:
            cart_list = json.loads(cart_str)
            cart_list[sku_id] = count
            cart_str = json.dumps(cart_list)
        response.set_cookie('cart', cart_str, expires=60*60*24*14)

    return response


def delete(request):
    """删除购物车"""
    if request.method != 'POST':
        return Http404()
    sku_id = request.POST.get('sku_id')
    response = JsonResponse({'status': 1})
    # redis删除
    if request.user.is_authenticated():
        redis_cli = get_redis_connection()
        redis_cli.hdel('cart%d' % request.user.id, sku_id)
        pass
    else:
        # cookies删除
        cart_str = request.COOKIES.get('cart')
        if cart_str:
            cart_list = json.loads(cart_str)
            cart_list.pop(sku_id)
            cart_str = json.dumps(cart_list)
        response.set_cookie('cart', cart_str, expires=60*60*24*14)

    return response
