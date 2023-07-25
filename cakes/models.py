from django.db import models


class Dough(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Shape(models.Model):
    shape = models.CharField(max_length=100, default='Квадрат')
    price = models.DecimalField(max_digits=6, decimal_places=2, default=400)

    def __str__(self):
        return f'{self.shape} +{self.price}'


class Level(models.Model):
    level = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=400)

    def __str__(self):
        return f'{str(self.level)} +{self.price}'


class Topping(models.Model):
    name = models.CharField(max_length=100, default='Без топпинга')
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.name}, +{self.price}'


class Berry(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f'{self.name}, +{self.price}'


class Decor(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f'{self.name}, +{self.price}'


class Inscription(models.Model):
    inscription = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=500)

    def __str__(self):
        return f'{self.inscription}, +{self.price}'


class Cake(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_custom = models.BooleanField(default=False)

    dough = models.ForeignKey(Dough, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.SET_DEFAULT, default=1)
    shape = models.ForeignKey(Shape, on_delete=models.SET_DEFAULT, default='Квадрат')
    topping = models.ManyToManyField('Topping', default='Без топпинга')
    berries = models.ManyToManyField('Berry', blank=True)
    decor = models.ManyToManyField('Decor', blank=True)

    def __str__(self):
        return f'{self.name}, {self.description}'


class Order(models.Model):
    customer_name = models.CharField(max_length=100)
    comment = models.CharField(max_length=250, blank=True)
    cake = models.ForeignKey(Cake, on_delete=models.CASCADE)
    delivery_address = models.TextField()
    delivery_date = models.DateField()
    delivery_time = models.TimeField()
    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    status = models.ForeignKey('OrderStatus', on_delete=models.SET_NULL, null=True)
    inscription = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f'Клиент: {self.customer_name}, Статус заказа: {self.status}, К оплате {self.total_price}'

    def calculate_total_price(self):
        cake_price = self.cake.price
        topping_price = sum(self.cake.topping.all().values_list('price', flat=True))
        berry_price = sum(self.cake.berries.all().values_list('price', flat=True))
        decor_price = sum(self.cake.decor.all().values_list('price', flat=True))
        inscription_price = 500 if self.inscription else 0
        return cake_price + topping_price + berry_price + decor_price + inscription_price

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)


class OrderStatus(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

