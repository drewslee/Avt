from django.db import models


class Supplier(models.Model):
    id_supplier = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256, null=False)


class Product(models.Model):
    id_product = models.AutoField(primary_key=True)
    name = models.CharField(max_length=10)


class Shipment(models.Model):
    id_shipment = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

class Customer(models.Model):
    id_customer = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256, null=False)
    id_shipment = models.ForeignKey(Shipment)

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
    id_trailer = models.ForeignKey(Trailer)
    pts = models.CharField(max_length=10, unique=True, blank=True)


class Race(models.Model):
    id_race = models.AutoField(primary_key=True)
    name_race = models.CharField(max_length=5)
    race_date = models.DateField()
    id_car = models.ForeignKey(Car)
    type_ship = models.BooleanField(default=0)
    supplier = models.ForeignKey(Supplier)
    customer = models.ForeignKey(Customer)
    product = models.ForeignKey(Product)
    mediator = models.ForeignKey(Mediator)
    driver = models.ForeignKey(Driver)
    milage = models.ForeignKey(Milage)
    weight_load = models.FloatField()
    weight_unload = models.FloatField()
    comm = models.TextField()
    state = models.IntegerField(default=0)
    create_time = models.DateTimeField(auto_now=True)
