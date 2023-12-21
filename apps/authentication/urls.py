from django.urls import include, path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name="login"),
    path('login', views.index, name="login"),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password', views.forgotPassword, name="forgot-password"),
    path('reset-password/<str:token>', views.resetPassword, name="reset-password"),
]
