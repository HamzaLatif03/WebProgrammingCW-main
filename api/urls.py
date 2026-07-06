"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.http import HttpResponse
from django.views.generic import RedirectView

from .import views


urlpatterns = [
    
    path('', views.main_spa,name='home'),
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico')),

    path('api/set-csrf-token/', views.set_csrf_token, name='set_csrf_token'),
    path('api/login/', views.login_view, name='login'),
    path('api/logout/', views.logout_view, name='logout'),
    path('api/user/', views.user, name='user'),
    path('api/signup/', views.signup_view, name='signup'),
    
    path('api/user-info/', views.user_info, name='user_info'),
    
    path('api/hobbies/', views.hobbies_list, name='hobbies_list'),
    
    path('api/similar-users/', views.similar_users, name='similar_users'),
    path('api/friendrelationships/', views.friend_relationships, name='friend_relationships'),
    path('api/friendrelationships/<int:relationship_id>/', views.update_friend_relationship, name='update_friend_relationship'),
]
    

