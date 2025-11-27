from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('menu/<int:table_id>/', views.menu, name='menu'),
    path('add-to-order/<int:table_id>/<int:item_id>/', views.add_to_order, name='add_to_order'),
    path('order/<int:order_id>/', views.view_order, name='view_order'),
    path('order/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    path('all-orders/', views.all_orders, name='all_orders'),
    path('delete-item/<int:item_id>/', views.delete_order_item, name='delete_order_item'),
]