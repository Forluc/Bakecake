from django.db import models

class Cake(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_custom = models.BooleanField(default=False)

    levels = models.IntegerField(choices=[(1, '1 уровень'), (2, '2 уровня'), (3, '3 уровня')], default=1)
    shape = models.CharField(max_length=100, choices=[('square', 'Квадрат'), ('round', 'Круг'), ('rectangle', 'Прямоугольник')], default='round')
    toppings = models.ManyToManyField('Topping', blank=True)
    berries = models.ManyToManyField('Berry', blank=True)
    decor = models.ManyToManyField('Decor', blank=True)
    inscription = models.CharField(max_length=100, blank=True)

class Topping(models.Model):
    name = models.CharField(max_length=100)

class Berry(models.Model):
    name = models.CharField(max_length=100)

class Decor(models.Model):
    name = models.CharField(max_length=100)

class Order(models.Model):
    customer_name = models.CharField(max_length=100)
    cake = models.ForeignKey(Cake, on_delete=models.CASCADE)
    delivery_address = models.TextField()
    delivery_date = models.DateField()
    delivery_time = models.TimeField()
    total_price = models.DecimalField(max_digits=6, decimal_places=2)
    status = models.ForeignKey('OrderStatus', on_delete=models.SET_NULL, null=True)

class OrderStatus(models.Model):
    name = models.CharField(max_length=100)
