from . import views
from django.urls import path
urlpatterns = [
    path('item/' , views.item_list),
    path('item/<int:pk>/' , views.item_detail),
    path('item/<int:pk>/report/', views.report_item),
]