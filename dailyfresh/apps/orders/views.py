from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django_redis import get_redis_connection
from .models import GoodsSKU, OrderInfo, OrderGoods
from django.http import Http404, HttpResponse, JsonResponse
import uuid
from django.db import transaction  # jango中引入事务
from django.db.models import F

# Create your views here.


@login_required
def index(request):
    """订单页"""
    # 获取订单商品
    sku_ids = request.GET.getlist("sku_id")
    if not sku_ids:
        return redirect('/cart')

    # 查询用户收货地址
    addr_list = request.user.address_set.all()

    # 查询订单商品明细
    sku_list = []
    redis_cli = get_redis_connection()
    key = 'cart%d' % request.user.id
    for sku_id in sku_ids:
        sku = GoodsSKU.objects.get(pk=sku_id)
        sku.count = redis_cli.hget(key, sku_id)
        sku_list.append(sku)

    context = {
        'title': '订单',
        'addr_list': addr_list,
        'sku_list': sku_list,
    }
    return render(request, 'place_order.html', context)


@login_required
@transaction.atomic  # 订单生成中加入事务
def handle(request):
    """处理订单"""
    if request.method != 'POST':
        return Http404()
    # 接收数据
    sku_str = request.POST.get('sku_list')
    addr_id = request.POST.get('addr')
    pay_style = request.POST.get('pay_style')
    # 后端有效性判断
    if not all([sku_str, addr_id, pay_style]):
        return JsonResponse({'status': 2})

    # 开启事务
    sid = transaction.savepoint()

    # 创建订单
    order = OrderInfo()
    order.order_id = str(uuid.uuid1())
    order.user = request.user
    order.address_id = int(addr_id)
    order.total_count = 0
    order.total_amount = 0
    order.trans_cost = 10
    order.pay_method = int(pay_style)
    # 支付编号
    order.save()

    # 遍历购买商品
    redis_cli = get_redis_connection()
    key = 'cart%d' % request.user.id
    sku_list = sku_str.split(',')
    sku_list.pop()
    # 设置变量保存订单状态,数量和总价
    order_status = True
    total_count = 0
    total_price = 0
    for sku_id in sku_list:
        # 判断库存
        sku = GoodsSKU.objects.get(pk=sku_id)
        cart_count = int(redis_cli.hget(key, sku_id))
        # if sku.stock >= cart_count:
        #     # 创建订单商品明细
        #     order_goods = OrderGoods()
        #     order_goods.order = order
        #     order_goods.sku = sku
        #     order_goods.count = cart_count
        #     order_goods.price = sku.price
        #     order_goods.save()
        #     # 更改库存,销量
        #     sku.stock -= cart_count
        #     sku.sales += cart_count
        #     sku.save()
        #     # 计算订单总数和总金额
        #     total_count += cart_count
        #     total_price += sku.price * cart_count
           # 下单完成删除订单
           # redis_cli.hdel(key, sku_id)

        # 高并发下修改变量会出现资源竞争的问题
        # 采用乐观锁, 行级锁, 同时只有一个在更新库存
        affect_rows = GoodsSKU.objects.filter(pk=sku_id, stock__gte=cart_count).update(stock=F('stock') - cart_count, sales=F('sales') + cart_count)
        if affect_rows:
            # 创建订单商品明细
            order_goods = OrderGoods()
            order_goods.order = order
            order_goods.sku = sku
            order_goods.count = cart_count
            order_goods.price = sku.price
            order_goods.save()
            # 计算订单总数和总金额
            total_count += cart_count
            total_price += sku.price * cart_count
        else:
            order_status = False
            break
    if order_status:
        order.total_count = total_count
        order.total_amount = total_price
        order.save()
        # 成功提交
        transaction.savepoint_commit(sid)
        # redis数据库不支持事务
        for sku_id in sku_list:
            redis_cli.hdel(key, sku_id)

        return JsonResponse({'status': 1})
    else:
        # 失败回滚
        transaction.savepoint_commit(sid)

        return JsonResponse({'status': 2})

