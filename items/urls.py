from . import views
from django.urls import path
urlpatterns = [
    path('item/' , views.item_list),
    path('item/<int:pk>/' , views.item_detail),
    path('my-items/', views.my_items),
]