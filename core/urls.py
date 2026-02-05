from django.contrib import admin
from django.urls import path
from api.routers import auth

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/auth/login/', auth.login, name='login'),
    path('api/auth/register/', auth.register, name='register'),
    path('api/auth/users/', auth.users_list, name='users_list'),
]
