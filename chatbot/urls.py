from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.chatbot_view, name='chatbot'),
    path('api/chat/', views.chat_api, name='chat_api'),
    path('api/user/', views.get_user_api, name='get_user'),
    path('api/quick/<str:action>/', views.quick_action, name='quick_action'),
    path('api/upload/', views.upload_file, name='upload_file'),  
]