# from django.urls import path
# from . import views

# app_name = 'admin'

# urlpatterns = [
#     # ========== مدیریت کاربران ==========
#     path('users/', views.user_list, name='user_list'),
#     path('users/<int:pk>/', views.user_detail, name='user_detail'),
#     path('users/<int:pk>/toggle-active/', views.user_toggle_active, name='user_toggle_active'),
#     path('users/<int:pk>/update/', views.user_update, name='user_update'),
    
#     # ========== مدیریت مقالات ==========
#     path('articles/', views.article_list, name='article_list'),
#     path('articles/<int:pk>/', views.article_detail, name='article_detail'),
#     path('articles/<int:pk>/toggle-publish/', views.article_toggle_publish, name='article_toggle_publish'),
#     path('articles/<int:pk>/delete/', views.article_delete, name='article_delete'),
    
#     # ========== مدیریت نظرات ==========
#     path('comments/', views.comment_list, name='comment_list'),
#     path('comments/<int:pk>/toggle-approve/', views.comment_toggle_approve, name='comment_toggle_approve'),
#     path('comments/<int:pk>/delete/', views.comment_delete, name='comment_delete'),
    
#     # ========== مدیریت ثبت‌نام‌های تخصصی ==========
#     path('signups/seo/', views.seo_signup_list, name='seo_signup_list'),
#     path('signups/ai/', views.ai_signup_list, name='ai_signup_list'),
#     path('signups/wordpress/', views.wordpress_signup_list, name='wordpress_signup_list'),
#     path('signups/ui/', views.ui_signup_list, name='ui_signup_list'),
#     path('signups/backend/', views.backend_signup_list, name='backend_signup_list'),
#     path('signups/frontend/', views.frontend_signup_list, name='frontend_signup_list'),
    
#     # ========== مدیریت درخواست‌های همکاری ==========
#     path('collaborations/', views.collaboration_list, name='collaboration_list'),
#     path('collaborations/<int:pk>/', views.collaboration_detail, name='collaboration_detail'),
#     path('collaborations/<int:pk>/update-status/', views.collaboration_update_status, name='collaboration_update_status'),
#     path('collaborations/<int:pk>/delete/', views.collaboration_delete, name='collaboration_delete'),
    
#     # ========== مدیریت پیام‌های تماس با ما ==========
#     path('contact-messages/', views.contact_message_list, name='contact_message_list'),
#     path('contact-messages/<int:pk>/delete/', views.contact_message_delete, name='contact_message_delete'),
    
#     # ========== مدیریت درخواست‌های مشاوره ==========
#     path('contact-requests/', views.contact_request_list, name='contact_request_list'),
#     path('contact-requests/<int:pk>/delete/', views.contact_request_delete, name='contact_request_delete'),
    
#     # ========== مدیریت درخواست‌های دوره ==========
#     path('study-requests/', views.study_request_list, name='study_request_list'),
#     path('study-requests/<int:pk>/', views.study_request_detail, name='study_request_detail'),
#     path('study-requests/<int:pk>/delete/', views.study_request_delete, name='study_request_delete'),
# ]


from django.urls import path
from . import views

app_name = "admin"

urlpatterns = [
    path("", views.media_library_list, name="list"),
    path('articles/', views.admin_add_blog_view, name='add_article'),
    path('tag/', views.admin_add_tag_view, name='add_tag'),
    path('category/', views.admin_add_category_view, name='add_category'),
    path('edit-blog/<slug:slug>/', views.admin_edit_blog_view, name='edit_blog'),
    path('delete-blog/<slug:slug>/', views.admin_delete_blog_view, name='delete_blog'),
    path("upload/", views.media_file_upload, name="upload"),
    path("<int:pk>/edit/", views.media_file_edit, name="edit"),
    path("<int:pk>/delete/", views.media_file_delete, name="delete"),
    path("comment/", views.comment_list, name="comment_list"),
    path("<int:pk>/approve/", views.comment_approve, name="approve"),
    path("<int:pk>/delete/", views.comment_delete, name="delete"),
    path("site-setting", views.site_settings_view, name="site_settings"),

]