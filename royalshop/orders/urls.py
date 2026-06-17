from django.urls import path
from . import views

urlpatterns = [
    path('cart/',                       views.cart_view,         name='cart'),
    path('cart/add/',                   views.cart_add,          name='cart_add'),
    path('cart/update/',                views.cart_update,       name='cart_update'),
    path('cart/remove/',                views.cart_remove,       name='cart_remove'),
    path('checkout/',                   views.checkout,          name='checkout'),
    path('place-order/',                views.place_order,       name='place_order'),
    path('confirmation/<int:order_id>/',views.order_confirmation,name='order_confirmation'),
    path('my-orders/',                  views.my_orders,         name='my_orders'),
]
