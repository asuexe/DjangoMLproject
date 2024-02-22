from django.urls import path
from . import views

urlpatterns = [
    path('index', views.home, name="index"),
    path('login',views.login,name='login'),
    path('signup',views.signup,name='signup'),
    path('logout',views.logout,name='logout'),
    path('',views.predict, name='predict')
]
