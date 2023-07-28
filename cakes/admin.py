from django.contrib import admin
from .models import Cake, Level, Shape, Topping, Berry, Decor, Inscription, Order, OrderStatus, TelegramUser

admin.site.register(TelegramUser)
admin.site.register(Cake)
admin.site.register(Inscription)
admin.site.register(Level)
admin.site.register(Shape)
admin.site.register(Topping)
admin.site.register(Berry)
admin.site.register(Decor)
admin.site.register(Order)
admin.site.register(OrderStatus)
