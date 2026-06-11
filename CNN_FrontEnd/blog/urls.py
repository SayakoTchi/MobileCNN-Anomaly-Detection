from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='blog/login.html'), name='login'),
    # 하단 탭 메뉴나 상세 기능으로 이동할 세부 경로 설정
    path('anomaly/', views.anomaly_view, name='anomaly'),      
    path('history/', views.history_view, name='history'),      
    path('settings/', views.settings_view, name='settings'),
    path('signup/', views.signup_view, name='signup'),
]