from django.urls import path 
from .views import *
# from . import views - > views.viewname.as_view()

urlpatterns = [

    path('login/',BaseLogin.as_view(),name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/',BaseRegister.as_view(),name='register'),
    
    path('',BaseHome.as_view(),name='home'),
    path('home/',BaseHome.as_view(),name='home'),


]
