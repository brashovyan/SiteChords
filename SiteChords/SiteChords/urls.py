"""SiteChords URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import re_path
from mainapp import views

urlpatterns = [
    path('admindjango/', admin.site.urls),
    path('', views.index, name='home'),
    path('content/<int:id>/', views.content, name='content'),
    path('create/', views.create, name="create"),
    path('register/', views.register, name='register'),
    path('login/', views.login1, name='login'),
    path('logout/', views.logout1, name='logout'),
    path('about/', views.about, name='about'),
    path('change/<int:id>/', views.change, name='change'),
    path('delete/<int:id>/', views.delete, name='delete'),
    path('profile/<int:id>/', views.profile, name='profile'),
    path('my/<int:id>/', views.my_songs, name='my_songs'),
    path('search/', views.search, name='search'),
    path('favourites/<int:id>/', views.favourites, name='favourites'),
    path('search/<str:search_str>/', views.search),
    path('my_favourites/<int:id>/', views.my_favourites, name='my_favourites'),
    path('admin/', views.admin, name='admin'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/delete/<int:id>/', views.admin_users_delete, name='admin_users_delete'),
    path('admin/users/delete_moder/<int:id>/', views.admin_users_deletemoder, name='admin_users_deletemoder'),
    path('admin/users/give_moder/<int:id>/', views.admin_users_givemoder, name='admin_users_givemoder'),
    path('admin/users/moder_list', views.admin_users_moderlist, name='admin_users_moderlist'),
]
