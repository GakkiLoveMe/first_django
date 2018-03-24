from django.conf.urls import url
from users import views


urlpatterns = [
    url(r'^register$', views.RegisterView.as_view()),  # 将类视图转换为视图函数
    url(r'^active/(.+)', views.active),
    url(r'^exists$', views.exists),
    url(r'^login$', views.LoginView.as_view()),
    url(r'^index$', views.index),
]