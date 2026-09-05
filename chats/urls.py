from rest_framework.urls import path
from . import views
urlpatterns =[
    path('conversations/' , views.chat_conv ),
    path('conversations/<int:pk>/messages/' , views.chat_msg),
    path('messages/<int:pk>/' , views.delete_msg),
    path('conversation/<int:pk>/block/' , views.block_unblock),
    
]