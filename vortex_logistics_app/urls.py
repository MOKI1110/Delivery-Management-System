from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('dcharge/', views.dcharge, name="dcharge"),
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    path('user_admin_login/', views.user_admin_login, name="user_admin_login"),
    path('user_home/', views.user_home, name="user_home"),
    path('user_view_delivery/',
         views.user_view_delivery,
         name="user_view_delivery"),
    path('admin_login/', views.admin_login, name="admin_login"),
    path('user_sign_up/', views.user_sign_up, name="user_sign_up"),
    path('user_sign_in/', views.user_sign_in, name="user_sign_in"),
    path('add_item/', views.add_item, name='add_item'),
    path('add_delivery/', views.add_delivery, name='add_delivery'),
    path('payment/', views.payment, name='payment'),
    path('admin_home/', views.admin_home, name='admin_home'),
    path('admin_view_delivery/',
         views.admin_view_delivery,
         name='admin_view_delivery'),
    path('calculate_delivery_charge/',
         views.calculate_delivery_charge,
         name='calculate_delivery_charge'),
    path('get_trip_details/', views.get_trip_details, name='get_trip_details'),
    path('update_delivery_status/', views.update_delivery_status, name='update_delivery_status'),
]
