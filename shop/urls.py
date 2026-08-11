from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.home, name='home'),
    path('save-order/', views.save_order, name='save_order'),
    path('services/', views.services_page_view, name='services'),
    path('services-wordpress/', views.services_wordpress_view, name='services_wordpress'),
    path('services-seo/', views.services_seo_view, name='services_seo'),
    path('services-web/', views.services_web_view, name='services_web'),
    path('services-digital/', views.services_digital_view, name='services_digital'),
    path('api/get-orders/', views.get_orders, name='get_orders'),
    path('api/save-selection/', views.save_selection, name='save_selection'),
    path('api/get-session-data/', views.get_session_data, name='get_session_data'),
    path('api/clear-session/', views.clear_session, name='clear_session'),
    path('templates/', views.template_list_view, name='template_list'),
    path('template-data/<int:template_id>/',
         views.template_data_view, name='template_data'),
    path('plans/', views.plan_list, name='plans'),
    path('plan-order/<str:plan_type>/', views.create_plan_order, name='create_plan_order'),
    # ===== مسیرهای پرداخت =====
    path('payment/status/<int:order_id>/', views.payment_status, name='payment_status'),
]
