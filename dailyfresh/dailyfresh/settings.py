"""
Django settings for dailyfresh project.

Generated by 'django-admin startproject' using Django 1.8.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, os.path.join(BASE_DIR, 'apps'))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 't7s!-#)zr#xj5r2dn$)gzy^eu*4!1ul_tvnp=#j64tdnr+81p('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
# DEBUG = False

ALLOWED_HOSTS = ['*',]


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'goods',
    'orders',
    'cart',
    'tinymce',
    'haystack',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'dailyfresh.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'dailyfresh.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        # 'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'NAME': 'dailyfresh',
        'PORT': '3306',
        'USER': 'root',
        'PASSWORD': 'mysql',
        'HOST': 'localhost',
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'zh-hans'  # 'en-us'

TIME_ZONE = 'Asia/Shanghai'  # 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'  # 用来判断是否为静态文件

# 设置静态文件加载路径
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

AUTH_USER_MODEL = 'users.User'  # 规定创建user的模型类

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 25
# 发送邮件的邮箱
EMAIL_HOST_USER = '18222549491@163.com'
# 在邮箱中设置的客户端授权密码
EMAIL_HOST_PASSWORD = 'jin199022'
# 收件人看到的发件人
EMAIL_FROM = '天天生鲜<18222549491@163.com>'

# 设置redis进行缓存
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/5",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}


# Session
# http://django-redis-chs.readthedocs.io/zh_CN/latest/#session-backend

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# 登陆验证时需配置,登录失败url
LOGIN_URL = '/users/login'

# 配置Django自定义的存储系统
DEFAULT_FILE_STORAGE = 'utils.storage.FdfsStorage'

# fdfs服务器配置文件路径
FDFS_CLIENT = os.path.join(BASE_DIR, 'utils/fdfs_client.conf')

# nginx获取的地址
FDFS_SERVER = 'http://127.0.0.1:8888/'

# 富文本设置
TINYMCE_DEFAULT_CONFIG = {
  'theme': 'advanced',  # 丰富样式
  'width': 600,
  'height': 400,
}

# 主页静态文件存储路径
GENERATE_HTML = os.path.join(BASE_DIR, 'static/html')

# 配置搜索引擎后端
HAYSTACK_CONNECTIONS = {
  'default': {
      # 使用whoosh引擎：提示，如果不需要使用jieba框架实现分词，就使用whoosh_backend
      'ENGINE': 'haystack.backends.whoosh_cn_backend.WhooshEngine',
      # 索引文件路径
      'PATH': os.path.join(BASE_DIR, 'whoosh_index'),
  }
}
# 当添加、修改、删除数据时，自动生成索引
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

# 设置结果显示页面，每页显示多少条数据
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 1
