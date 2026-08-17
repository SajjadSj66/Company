from django.contrib import admin
from users.views import *
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from shop.views import *
from myadmin import views as settings_views
from django.contrib.sitemaps.views import sitemap
from myadmin.sitemaps import PostSitemap

sitemaps = {"posts": PostSitemap}


urlpatterns = [
    path('', home_view, name='home'),
    path('sijeey/', admin.site.urls),
    path('admin-dashboard/', include("myadmin.urls")),
    path("users/", include("users.urls")),
    path('course/', include("educate.urls")),
    # path('shop/', include("shop.urls")),
    path('payment/verify/', payment_verify, name='payment_verify'),
    path('services', services_page_view, name='services'),
    path('services-wordpress/', services_wordpress_view, name='services_wordpress'),
    path('services-seo/', services_seo_view, name='services_seo'),
    path('services-web/', services_web_view, name='services_web'),
    path('services-digital/', services_digital_view, name='services_digital'),
    path('services-support/', services_support_view, name='services_support'),
    path('templates/', template_list_view, name='template_list'),
    # ========== چت‌بات ==========
    path('chatbot/', include('chatbot.urls')), 
    path("robots.txt", settings_views.robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)