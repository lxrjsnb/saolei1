from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # 注册功能已禁用，只允许数据库中已存在的用户登录
    # path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),
]
