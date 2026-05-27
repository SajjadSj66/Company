from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    # نمایش دوره‌ها
    path('', views.CourseListView.as_view(), name='course_list'),
    path('<slug:slug>/', views.CourseDetailView.as_view(), name='course_detail'),
    
    # سبد خرید
    path('add-to-cart/<slug:slug>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # تسویه و سفارش
    path('checkout/', views.checkout, name='checkout'),
    path('payment/<int:order_id>/', views.payment, name='payment'),
    path('orders/', views.order_history, name='order_history'),
]