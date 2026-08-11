from django.contrib import admin
from users.views import home_view
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from shop.views import payment_verify

urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path("users/", include("users.urls")),
    path('course/', include("educate.urls")),
    path('shop/', include("shop.urls")),
    path('payment/verify/', payment_verify, name='payment_verify'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
