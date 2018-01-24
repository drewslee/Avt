from django.db import models
from datetime import date
from django.shortcuts import reverse


class Constants(models.Model):
    organization_unit_full = models.CharField(max_length=256)
    organization_unit_small = models.CharField(max_length=50)
    mechanic = models.CharField(max_length=50)
    dispatcher = models.CharField(max_length=50)


class Supplier(models.Model):
    id_supplier = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256, verbose_name='Поставщик')
    inn = models.DecimalField(max_digits=12, decimal_places=0, unique=True, null=True, blank=True, verbose_name='ИНН')

    def __str__(self):
        return '%s' % self.name

    def get_absolute_url(self):
        return reverse('SupplierList', kwargs={'pk': self.pk})

    def __iter__(self):
        for field in self._meta.fields:
            yield (field.verbose_name, field.value_to_string(self))


class Product(models.Model):
    id_product = models.AutoField(primary_key=True)
    name = models.CharField(max_length=10, verbose_name='Груз')

    def __str__(self):
        return '%s' % self.name

    def get_absolute_url(self):
        return reverse('ProductList', kwargs={'pk': self.pk})


class Shipment(models.Model):
    id_shipment = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name='Место разгрузки')

    def __str__(self):
        return '%s' % self.name

    def get_absolute_url(self):
        return reverse('ShipmentList', kwargs={'pk': self.pk})


class Customer(models.Model):
    id_customer = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256,  verbose_name='Клиент')
    inn = models.DecimalField(max_digits=12, decimal_places=0, unique=True, null=True, blank=True, verbose_name='ИНН')

    def __str__(self):
        return '%s' % self.name

    def get_absolute_url(self):
        return reverse('CustomerList', kwargs={'pk': self.pk})


class Mediator(models.Model):
    id_mediator = models.AutoField(primary_key=True)
    address = models.CharField(max_length=256, verbose_name='Посредник')
    inn = models.DecimalField(max_digits=12, decimal_places=0, unique=True, null=True, blank=True, verbose_name='ИНН')

    def __str__(self):
        return '%s' % self.address

    def get_absolute_url(self):
        return reverse('MediatorList', kwargs={'pk': self.pk})


class Driver(models.Model):
    id_driver = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, verbose_name='Водитель')

    def __str__(self):
        return '%s' % self.name

    def get_absolute_url(self):
        return reverse('DriverList', kwargs={'pk': self.pk})


class Trailer(models.Model):
    id_trailer = models.AutoField(primary_key=True)
    number = models.CharField(max_length=10)

    def __str__(self):
        return '%s' % self.number

    def get_absolute_url(self):
        return reverse('TrailerList', kwargs={'pk': self.pk})


class Car(models.Model):
    id_car = models.AutoField(primary_key=True)
    number = models.CharField(max_length=11, unique=True, verbose_name='Номер машины')
    brand = models.CharField(max_length=20, default='Scania')


    pts = models.CharField(max_length=10, null=True, blank=True, verbose_name='ПТС')
    trailer = models.ForeignKey(Trailer, blank=True, null=True)
    mediator = models.ForeignKey(Mediator, blank=True, null=True)

    def __str__(self):
        return '%s' % self.number

    def get_absolute_url(self):
        return reverse('CarList', kwargs={'pk': self.pk})


class Race(models.Model):
    CREATE = 'Создан'
    LOAD = 'Загружен'
    UNLOAD = 'Выгружен'
    FINISH = 'Закончен'
    END = 'Проведен'
    ACCIDENT = 'Авария'
    STATE = (
        (CREATE, 'Создан'),
        (LOAD, 'Зазгружен'),
        (UNLOAD, 'Выгружен'),
        (FINISH, 'Закончена'),
        (END, 'Проведена'),
        (ACCIDENT, 'Авария'),
    )
    TYPE = (
        ('Реализация', 'Реализация'),
        ('Услуга', 'Услуга')
    )
    id_race = models.AutoField(primary_key=True)
    name_race = models.CharField(max_length=5, default='Рейс')
    race_date = models.DateField(default=date.today)
    car = models.ForeignKey(Car)
    driver = models.ForeignKey(Driver)
    type_ship = models.CharField(default=TYPE[0], choices=TYPE, max_length=10)
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
    state = models.CharField(default=STATE[0], choices=STATE, max_length=9)
    shoulder = models.FloatField(default=0)
    create_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s' % self.name_race

    def get_absolute_url(self):
        return reverse('RaceUpdate', kwargs={'pk': self.pk})

 #   @property
 #   def get_sum_weight(self):
 #       self.weight_load

