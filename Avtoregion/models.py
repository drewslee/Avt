from django.db import models


class Supplier(models.Model):
    id_supplier = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)


class Product(models.Model):
    id_product = models.AutoField(primary_key=True)
    name = models.CharField(max_length=10)


class Shipment(models.Model):
    id_shipment = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)


class Customer(models.Model):
    id_customer = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)


class Mediator(models.Model):
    id_mediator = models.AutoField(primary_key=True)
    address = models.CharField(max_length=256)


class Driver(models.Model):
    id_driver = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)


class Milage(models.Model):
    id_milage = models.AutoField(primary_key=True)
    id_driver = models.ForeignKey(Driver)
    start_milage = models.IntegerField()
    end_milage = models.IntegerField()


class Trailer(models.Model):
    id_trailer = models.AutoField(primary_key=True)
    number = models.CharField(max_length=10)


class Car(models.Model):
    id_car = models.AutoField(primary_key=True)
    number = models.CharField(max_length=10, unique=True)
    pts = models.CharField(max_length=10, unique=True, blank=True)
    trailer = models.ForeignKey(Trailer, blank=True, null=True)


class Race(models.Model):
    id_race = models.AutoField(primary_key=True)
    name_race = models.CharField(max_length=5)
    race_date = models.DateField()
    car = models.ForeignKey(Car)
    driver = models.ForeignKey(Driver)
    type_ship = models.BooleanField(default=0)
    supplier = models.ForeignKey(Supplier)
    customer = models.ForeignKey(Customer)
    shipment = models.ForeignKey(Shipment, null=True, blank=True)
    product = models.ForeignKey(Product)
    mediator = models.ForeignKey(Mediator)
    s_milage = models.FloatField(default=0)
    e_milage = models.FloatField(default=0)
    weight_load = models.FloatField(default=0)
    weight_unload = models.FloatField(default=0)
    comm = models.TextField()
    state = models.IntegerField(default=0)
    create_time = models.DateTimeField(auto_now=True)
