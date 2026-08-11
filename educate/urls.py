from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.amozesh_page, name='course_list'),
    path('seo-signup/', views.seo_signup, name='seo_signup'),
    path('ai-signup/', views.ai_signup, name='ai_signup'),
    path('worpress-signup/', views.wordpress_signup, name='wordpress_signup'),
    path('ui-signup/', views.ui_signup, name='ui_signup'),
    path('back-signup/', views.back_signup, name='back_signup'),
    path('front-signup/', views.front_signup, name='front_signup'),
    path('buy-course/<int:course_id>/', views.create_course_order, name='buy_course'),
    path('<slug:slug>/', views.course_detail, name='course_detail'),
    path('buy/<slug:slug>/', views.buy_course_by_slug, name='buy_course_by_slug'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('add-to-cart/<slug:slug>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/<int:order_id>/', views.payment, name='payment'),
    path('orders/', views.order_history, name='order_history'),
]