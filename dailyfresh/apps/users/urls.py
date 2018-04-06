from django.conf.urls import url
from users import views
from django.contrib.auth.decorators import login_required


urlpatterns = [
    url(r'^register$', views.RegisterView.as_view()),  # 将类视图转换为视图函数
    url(r'^active/(.+)', views.active),
    url(r'^exists$', views.exists),
    url(r'^login$', views.LoginView.as_view()),
    url(r'^logout$', views.logout_user),
    url(r'^info$', views.info),
    url(r'^order$', views.OrderView.as_view()),
    # url(r'^site$', login_required(views.SiteView.as_view())),  # 类视图添加装饰器
    url(r'site$', views.SiteView.as_view()),
    url(r'^area$', views.area),
]