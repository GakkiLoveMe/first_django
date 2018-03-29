from django.contrib import admin
from .models import Goods, GoodsSKU, IndexGoodsBanner, IndexCategoryGoodsBanner, IndexPromotionBanner, GoodsImage, GoodsCategory
from celery_tasks.tasks import generate_index
from django.core.cache import cache

# Register your models here.


# 创建模型管理类
class BaseAdmin(admin.ModelAdmin):
    """创建模型管理基类"""
    # 根据模型类的修改生成不同的主页
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj,form, change)

        # celery 异步生成主页
        generate_index.delay()

        # 更改后删除缓存
        cache.delete('index')

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        generate_index.delay()
        cache.delete("index")


class IndexCategoryGoodsBannerAdmin(BaseAdmin):
    pass


class IndexPromotionBannerAdmin(BaseAdmin):
    pass


class IndexGoodsBannerAdmin(BaseAdmin):
    pass


class GoodsCategoryAdmin(BaseAdmin):
    pass


class GoodsSKUAdmin(BaseAdmin):
    pass


admin.site.register(Goods)
admin.site.register(GoodsSKU, GoodsSKUAdmin)
admin.site.register(IndexPromotionBanner, IndexPromotionBannerAdmin)
admin.site.register(IndexCategoryGoodsBanner, IndexCategoryGoodsBannerAdmin)
admin.site.register(IndexGoodsBanner, IndexGoodsBannerAdmin)
admin.site.register(GoodsImage)
admin.site.register(GoodsCategory, GoodsCategoryAdmin)

