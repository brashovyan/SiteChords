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
    path('admin/', admin.site.urls),
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
]
