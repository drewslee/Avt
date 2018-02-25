from django.db import models
from datetime import date
from django.utils import timezone
from django.shortcuts import reverse


class Constants(models.Model):
    organization_unit_full = models.CharField(max_length=256, blank=True)
    organization_unit_small = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=256, blank=True)
    mechanic = models.CharField(max_length=50, blank=True)
    dispatcher = models.CharField(max_length=50, blank=True)
    ogrn = models.CharField(max_length=13, blank=True)


class Supplier(models.Model):
    id_supplier = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256, verbose_name='Поставщик')
    address = models.CharField(max_length=256, blank=True)
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
    name = models.CharField(max_length=20, verbose_name='Название')

    def __str__(self):
        return '%s' % self.name

    def get_absolute_url(self):
        return reverse('ProductList', kwargs={'pk': self.pk})


class LoadingPlace(models.Model):
    id_load_place = models.AutoField(primary_key=True)
    supplier = models.ForeignKey('Supplier')
    address = models.CharField(max_length=255, verbose_name='Место загрузки')

    def __str__(self):
        return '%s' % self.address


class Shipment(models.Model):
    id_shipment = models.AutoField(primary_key=True)
    customer = models.ForeignKey('Customer')
    name = models.CharField(max_length=100, verbose_name='Место разгрузки')

    def __str__(self):
        return '%s' % self.name

    def get_absolute_url(self):
        return reverse('ShipmentList', kwargs={'pk': self.pk})


class Customer(models.Model):
    id_customer = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256, verbose_name='Клиент')
    address = models.CharField(max_length=256, blank=True)
    inn = models.DecimalField(max_digits=12, decimal_places=0, unique=True, null=True, blank=True, verbose_name='ИНН')

    def __str__(self):
        return '%s' % self.name

    def get_absolute_url(self):
        return reverse('CustomerList', kwargs={'pk': self.pk})


class Mediator(models.Model):
    id_mediator = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name='Название', blank=True)
    address = models.CharField(max_length=256, verbose_name='Посредник')
    inn = models.DecimalField(max_digits=12, decimal_places=0, unique=True, null=True, blank=True, verbose_name='ИНН')

    def __str__(self):
        return '%s' % self.address

    def get_absolute_url(self):
        return reverse('MediatorList', kwargs={'pk': self.pk})


class Driver(models.Model):
    id_driver = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, verbose_name='Водитель')
    full_name = models.CharField(max_length=100, blank=True)
    driver_card = models.CharField(max_length=50, blank=True)
    personnel_number = models.DecimalField(decimal_places=0, max_digits=10, blank=True, default=0)
    date_med = models.DateField(blank=True)

    def __str__(self):
        return '%s' % self.name

    def get_absolute_url(self):
        return reverse('DriverList', kwargs={'pk': self.pk})


class Trailer(models.Model):
    id_trailer = models.AutoField(primary_key=True)
    number = models.CharField(max_length=10)
    brand_trailer = models.CharField(max_length=10, default='85300F')
    garage_number_trailer = models.DecimalField(max_digits=10, decimal_places=0, max_length=5, blank=True, default=0)

    def __str__(self):
        return '%s' % self.number

    def get_absolute_url(self):
        return reverse('TrailerList', kwargs={'pk': self.pk})


class Car(models.Model):
    id_car = models.AutoField(primary_key=True)
    number = models.CharField(max_length=11, unique=True, verbose_name='Номер машины')
    pts = models.CharField(max_length=10, null=True, blank=True, verbose_name='ПТС')
    brand = models.CharField(max_length=20, default='Scania')
    garage_number = models.DecimalField(max_digits=10, decimal_places=0, max_length=5, blank=True, default=0)
    trailer = models.ForeignKey(Trailer, blank=True, null=True)
    mediator = models.ForeignKey(Mediator, blank=True, null=True)

    def __str__(self):
        return '%s' % self.number

    def get_absolute_url(self):
        return reverse('CarList', kwargs={'pk': self.pk})


class Units(models.Model):
    name = models.CharField(max_length=10)
    short_name = models.CharField(max_length=3, blank=True)

    def __str__(self):
        return '%s' % self.short_name

    def get_absolute_url(self):
        return reverse('UnitList', kwargs={'pk': self.pk})


class Race(models.Model):
    CREATE = 'Создан'
    LOAD = 'Загружен'
    UNLOAD = 'Выгружен'
    FINISH = 'Закончен'
    END = 'Проведен'
    ACCIDENT = 'Авария'
    STATE = (
        (CREATE, 'Создан'),
        (LOAD, 'Загружен'),
        (UNLOAD, 'Выгружен'),
        (FINISH, 'Закончен'),
        (END, 'Проведен'),
        (ACCIDENT, 'Авария'),
    )
    TYPE = (
        ('Реализация', 'Реализация'),
        ('Услуга', 'Услуга')
    )
    CUSTOMER = 'Поставщик'
    CLIENT = 'Покупатель'
    ORDER = (
        (CUSTOMER, 'Поставщик'),
        (CLIENT, 'Покупатель')
    )
    id_race = models.AutoField(primary_key=True)
    race_date = models.DateTimeField(default=timezone.now)
    arrival_time = models.DateTimeField(default=timezone.now)
    car = models.ForeignKey(Car)
    driver = models.ForeignKey(Driver)
    type_ship = models.CharField(default=TYPE[0], choices=TYPE, max_length=10)
    supplier = models.ForeignKey(Supplier)
    place_load = models.ForeignKey(LoadingPlace, null=True, blank=True)
    customer = models.ForeignKey(Customer)
    order_type_race = models.CharField(default=ORDER[0], choices=ORDER, max_length=256)
    shipment = models.ForeignKey(Shipment, null=True, blank=True)
    product = models.ForeignKey(Product)
    mediator = models.ForeignKey(Mediator, null=True, blank=True)
    s_milage = models.FloatField(default=0)
    e_milage = models.FloatField(default=0)
    weight_load = models.FloatField(default=0)
    unit_load = models.ForeignKey(Units, null=True, blank=True, related_name='unit_load')
    weight_unload = models.FloatField(default=0)
    unit_unload = models.ForeignKey(Units, null=True, blank=True, related_name='unit_unload')
    comm = models.TextField(null=True, blank=True)
    state = models.CharField(default=STATE[0], choices=STATE, max_length=9)
    gas_start = models.DecimalField(max_digits=5, decimal_places=0, default=0)
    gas_end = models.DecimalField(max_digits=5, decimal_places=0, default=0)
    gas_given = models.DecimalField(max_digits=5, decimal_places=0, default=0)
    shoulder = models.FloatField(default=0)
    create_time = models.DateTimeField(auto_now=True)

    class Meta:
        get_latest_by = 'race_date'

    def __str__(self):
        return '%s' % self.id_race

    def get_absolute_url(self):
        return reverse('RaceUpdate', kwargs={'pk': self.pk})

    def get_foreign_fields(self):
        return [getattr(self, f.name) for f in self._meta.fields if type(f) == models.fields.related.ForeignKey]

    @property
    def gas_spent(self):
        return self.gas_start + self.gas_given - self.gas_end

    @property
    def track(self):
        if self.e_milage > self.s_milage:
            track = self.e_milage - self.s_milage
        else:
            track = 0
        return track

    @property
    def get_supplier_name(self):
        return self.supplier.name

    @property
    def get_shipper(self):
        if self.mediator is None and (self.type_ship == self.TYPE[0][0]):
            return Constants.organization_unit_full + ", " + Constants.address
        if self.mediator is not None and (self.type_ship == self.TYPE[0][0]):
            return Constants.organization_unit_full + ", " + Constants.address
        if self.mediator is None and (self.type_ship == self.TYPE[1][0]) and (self.order_type_race == self.ORDER[0][0]):
            return self.supplier.name + " " + self.supplier.address
        if self.mediator is not None and (self.type_ship == self.TYPE[1][0]) and \
                (self.order_type_race == self.ORDER[0][0]):
            return self.supplier.name + " " + self.supplier.address
        if self.mediator is not None and (self.type_ship == self.TYPE[1][0]) and \
                (self.order_type_race == self.ORDER[1][1]):
            return self.customer.name + " " + self.customer.address

    @property
    def get_consignee(self):
            return self.customer.name + ", " + self.customer.address

    @property
    def get_car(self):
        return self.car.brand + " " + self.car.number + " " + self.car.trailer.number
