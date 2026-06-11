"""
URL configuration for on_device_prj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 1) /blog/로 시작하는 주소는 blog 앱의 urls.py로 토스
    path('blog/', include('blog.urls')),
    
    # 2) 루트 주소('')나 /login/ 등 공통 주소도 그냥 앱 내부에서 처리하도록 통째로 토스
    path('', include('blog.urls')), 
]
