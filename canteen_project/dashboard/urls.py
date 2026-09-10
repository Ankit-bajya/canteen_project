# dashboard/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('add-to-cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
    path('my-orders/', views.my_orders, name='my_orders'),
    # dashboard/urls.py
    path('kitchen/', views.kitchen_dashboard, name='kitchen_dashboard'),
    path('kitchen/update-status/<int:order_id>/<str:status>/', views.update_order_status, name='update_order_status'),
    path('kitchen/toggle-item/<int:item_id>/', views.toggle_item_availability, name='toggle_item_availability'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('notifications/', views.notifications_view, name='notifications'),
]