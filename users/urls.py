from django.urls import path
from . import views

app_name = 'users'
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('about/', views.about_view, name='about'),
    path('send-otp/', views.send_otp_view, name='send_otp'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('verify-otp-submit/', views.verify_otp_submit, name='verify_otp_submit'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('logout/', views.logout_view, name='logout'),
    path('contact/', views.contact_view, name='contact_page'),
    path('course-registration/', views.course_registration_view,
         name='course_registration'),
    path('contact-request/', views.contact_request_view, name='contact_request'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('collaboration/', views.collaboration_view, name='collaboration'),
    path('blog/', views.blog_home, name='blog_home'),
    path('blog/filter/', views.blog_filter, name='blog_filter'),
    path('blog/search/', views.blog_search, name='blog_search'),
    path('blog/category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('blog/article/<slug:slug>/', views.article_detail, name='article_detail'),
]
