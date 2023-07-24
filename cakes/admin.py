from django.contrib import admin
from .models import Cake, Topping, Berry, Decor, Order, OrderStatus



admin.site.register(Cake)
admin.site.register(Topping)
admin.site.register(Berry)
admin.site.register(Decor)
admin.site.register(Order)
admin.site.register(OrderStatus)
