from django.contrib import admin
from .models import Goods, GoodsSKU, IndexGoodsBanner, IndexCategoryGoodsBanner, IndexPromotionBanner, GoodsImage, GoodsCategory

# Register your models here.

admin.site.register(Goods)
admin.site.register(GoodsSKU)
admin.site.register(IndexPromotionBanner)
admin.site.register(IndexCategoryGoodsBanner)
admin.site.register(IndexGoodsBanner)
admin.site.register(GoodsImage)
admin.site.register(GoodsCategory)

