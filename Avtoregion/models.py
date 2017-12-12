from django.db import models
from datetime import date
from django.shortcuts import reverse


class Supplier(models.Model):
    id_supplier = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)
    inn = models.DecimalField(max_digits=12, decimal_places=0, unique=True, null=True)

    def __str__(self):
        return '%s' % self.name

    def get_absolute_url(self):
        return reverse('Supplier', kwargs={'pk': self.pk})


class Product(models.Model):
    id_product = models.AutoField(primary_key=True)
    name = models.CharField(max_length=10)

    def __str__(self):
        return '%s' % self.name

    def get_absolute_url(self):
        return reverse('Product', kwargs={'pk': self.pk})


class Shipment(models.Model):
    id_shipment = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return '%s' % self.name

    def get_absolute_url(self):
        return reverse('Shipment', kwargs={'pk': self.pk})


class Customer(models.Model):
    id_customer = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)

    def __str__(self):
        return '%s' % self.name

    def get_absolute_url(self):
        return reverse('Customer', kwargs={'pk': self.pk})


class Mediator(models.Model):
    id_mediator = models.AutoField(primary_key=True)
    address = models.CharField(max_length=256)

    def __str__(self):
        return '%s' % self.address

    def get_absolute_url(self):
        return reverse('Mediator', kwargs={'pk': self.pk})


class Driver(models.Model):
    id_driver = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return '%s' % self.name

    def get_absolute_url(self):
        return reverse('Driver', kwargs={'pk': self.pk})


class Milage(models.Model):
    id_milage = models.AutoField(primary_key=True)
    id_driver = models.ForeignKey(Driver)
    start_milage = models.IntegerField()
    end_milage = models.IntegerField()


class Trailer(models.Model):
    id_trailer = models.AutoField(primary_key=True)
    number = models.CharField(max_length=10)

    def __str__(self):
        return '%s' % self.number

    def get_absolute_url(self):
        return reverse('Trailer', kwargs={'pk': self.pk})


class Car(models.Model):
    id_car = models.AutoField(primary_key=True)
    number = models.CharField(max_length=10, unique=True, verbose_name='Номер машины')
    pts = models.CharField(max_length=10, unique=True, blank=True)
    trailer = models.ForeignKey(Trailer, blank=True, null=True)

    def __str__(self):
        return '%s' % self.number

    def get_absolute_url(self):
        return reverse('Car', kwargs={'pk': self.pk})

class Race(models.Model):
    id_race = models.AutoField(primary_key=True)
    name_race = models.CharField(max_length=5, default='Рейс')
    race_date = models.DateField(default=date.today)
    car = models.ForeignKey(Car)
    driver = models.ForeignKey(Driver)
    type_ship = models.BooleanField(default=0)
    supplier = models.ForeignKey(Supplier)
    customer = models.ForeignKey(Customer)
    shipment = models.ForeignKey(Shipment, null=True, blank=True)
    product = models.ForeignKey(Product)
    mediator = models.ForeignKey(Mediator, null=True, blank=True)
    s_milage = models.FloatField(default=0)
    e_milage = models.FloatField(default=0)
    weight_load = models.FloatField(default=0)
    weight_unload = models.FloatField(default=0)
    comm = models.TextField(null=True, blank=True)
    state = models.IntegerField(default=0)
    create_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s' % self.name_race

    def get_absolute_url(self):
        return reverse('Race', kwargs={'pk': self.pk})
