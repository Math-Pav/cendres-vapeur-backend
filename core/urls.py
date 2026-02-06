from django.contrib import admin
from django.urls import path
from api.router import auth

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/auth/login/', auth.login, name='login'),
    path('api/auth/verify-2fa/', auth.verify_2fa, name='verify_2fa'),
    path('api/auth/register/', auth.register, name='register'),
    path('api/auth/users/', auth.users_list, name='users_list'),
]
