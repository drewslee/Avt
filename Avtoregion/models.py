from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.shortcuts import reverse


class Constants(models.Model):
    organization_unit_full = models.CharField(max_length=256, blank=True)
    organization_unit_small = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=256, blank=True)
    mechanic = models.CharField(max_length=50, blank=True)
    medic = models.CharField(max_length=50, blank=True)
    dispatcher = models.CharField(max_length=50, blank=True)
    ogrn = models.CharField(max_length=13, blank=True)


class Supplier(models.Model):
    id_supplier = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256, verbose_name='Поставщик')
    address = models.CharField(max_length=256, blank=True)
    inn = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        unique=True,
        null=True,
        blank=True,
        verbose_name='ИНН')
    has_deleted = models.BooleanField(default=False)

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
    has_deleted = models.BooleanField(default=False)

    def __str__(self):
        return '%s' % self.name

    def get_absolute_url(self):
        return reverse('ProductList', kwargs={'pk': self.pk})


class LoadingPlace(models.Model):
    id_load_place = models.AutoField(primary_key=True)
    supplier = models.ForeignKey('Supplier')
    address = models.CharField(max_length=255, verbose_name='Место загрузки')
    has_deleted = models.BooleanField(default=False)

    def __str__(self):
        return '%s' % self.address


class Shipment(models.Model):
    id_shipment = models.AutoField(primary_key=True)
    customer = models.ForeignKey('Customer')
    name = models.CharField(max_length=100, verbose_name='Место разгрузки')
    has_deleted = models.BooleanField(default=False)

    def __str__(self):
        return '%s' % self.name

    def get_absolute_url(self):
        return reverse('ShipmentList', kwargs={'pk': self.pk})


class Customer(models.Model):
    id_customer = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256, verbose_name='Клиент')
    address = models.CharField(max_length=256, blank=True)
    inn = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        unique=True,
        null=True,
        blank=True,
        verbose_name='ИНН')
    has_deleted = models.BooleanField(default=False)

    def __str__(self):
        return '%s' % self.name

    def get_absolute_url(self):
        return reverse('CustomerList', kwargs={'pk': self.pk})


class Mediator(models.Model):
    id_mediator = models.AutoField(primary_key=True)
    name = models.CharField(
        max_length=100,
        verbose_name='Название',
        blank=True)
    address = models.CharField(max_length=256, verbose_name='Посредник')
    inn = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        unique=True,
        null=True,
        blank=True,
        verbose_name='ИНН')
    has_deleted = models.BooleanField(default=False)

    def __str__(self):
        return '%s' % self.name

    def get_absolute_url(self):
        return reverse('MediatorList', kwargs={'pk': self.pk})


class Groups(models.Model):
    name = models.CharField(max_length=50, verbose_name='Группы')

    def __str__(self):
        return '%s'.format(self.name)


class Driver(models.Model):
    id_driver = models.AutoField(primary_key=True)
    group = models.ForeignKey(Groups, blank=True, null=True)
    name = models.CharField(max_length=50, verbose_name='Водитель')
    full_name = models.CharField(max_length=100, blank=True)
    driver_card = models.CharField(max_length=50, blank=True)
    personnel_number = models.DecimalField(
        decimal_places=0, max_digits=10, blank=True, default=0)
    date_med = models.DateField(blank=True)
    has_deleted = models.BooleanField(default=False)

    def __str__(self):
        return '%s' % self.name

    def get_absolute_url(self):
        return reverse('DriverList', kwargs={'pk': self.pk})


class Trailer(models.Model):
    id_trailer = models.AutoField(primary_key=True)
    number = models.CharField(max_length=10)
    brand_trailer = models.CharField(max_length=10, default='85300F')
    garage_number_trailer = models.DecimalField(
        max_digits=10, decimal_places=0, max_length=5, blank=True, default=0)
    has_deleted = models.BooleanField(default=False)

    def __str__(self):
        return '%s' % self.number

    def get_absolute_url(self):
        return reverse('TrailerList', kwargs={'pk': self.pk})


class Car(models.Model):
    id_car = models.AutoField(primary_key=True)
    number = models.CharField(
        max_length=11,
        unique=True,
        verbose_name='Номер машины')
    pts = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name='ПТС')
    brand = models.CharField(max_length=20, default='Scania')
    garage_number = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        max_length=5,
        blank=True,
        default=0)
    trailer = models.ForeignKey(Trailer, blank=True, null=True)
    mediator = models.ForeignKey(Mediator, blank=True, null=True)
    has_deleted = models.BooleanField(default=False)

    def __str__(self):
        return '%s' % self.number

    def get_absolute_url(self):
        return reverse('CarList', kwargs={'pk': self.pk})


class Units(models.Model):
    name = models.CharField(max_length=10)
    short_name = models.CharField(max_length=3, blank=True)
    has_deleted = models.BooleanField(default=False)

    def __str__(self):
        return '%s' % self.short_name

    def get_absolute_url(self):
        return reverse('UnitList', kwargs={'pk': self.pk})


class Race(models.Model):
    UNHANDLED = 'Не проведен'
    HANDLE_SUP = 'Поставщик'
    HANDLE_CUS = 'Покупатель'
    HANDLE_ALL = 'Поставщик/Покупатель'
    STATE_ACC = (
        (UNHANDLED, ''),
        (HANDLE_SUP, 'По поставщику'),
        (HANDLE_CUS, 'По покупателю'),
        (HANDLE_ALL, 'Проведен')
    )
    CREATE = 'Создан'
    ACCEPTED = 'Принят'
    LOAD = 'Загружен'
    UNLOAD = 'Выгружен'
    FINISH = 'Закончен'
    CHECKED = 'Сверен'
    END = 'Проведен'
    ACCIDENT = 'Авария'
    STATE = (
        (CREATE, 'Создан'),
        (ACCEPTED, 'Принят'),
        (LOAD, 'Загружен'),
        (UNLOAD, 'Выгружен'),
        (FINISH, 'Закончен'),
        (CHECKED, 'Сверен'),
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
    ttn_number = models.CharField(max_length=50, blank=True)
    car = models.ForeignKey(Car)
    driver = models.ForeignKey(Driver)
    type_ship = models.CharField(default=TYPE[0], choices=TYPE, max_length=10)
    supplier = models.ForeignKey(Supplier)
    place_load = models.ForeignKey(LoadingPlace, null=True, blank=True)
    customer = models.ForeignKey(Customer)
    order_type_race = models.CharField(
        default=ORDER[0], choices=ORDER, max_length=256)
    shipment = models.ForeignKey(Shipment, null=True, blank=True)
    product = models.ForeignKey(Product)
    s_milage = models.DecimalField(default=0, max_digits=8, decimal_places=0)
    e_milage = models.DecimalField(default=0, max_digits=8, decimal_places=0)
    weight_load = models.FloatField(default=0)
    unit_load = models.ForeignKey(
        Units,
        null=True,
        blank=True,
        related_name='unit_load')
    weight_unload = models.FloatField(default=0)
    unit_unload = models.ForeignKey(
        Units,
        null=True,
        blank=True,
        related_name='unit_unload')
    comm = models.TextField(null=True, blank=True)
    state = models.CharField(default=STATE[0], choices=STATE, max_length=9)
    fulfill = models.CharField(default=STATE_ACC[0], choices=STATE_ACC, max_length=255, blank=True)
    gas_start = models.DecimalField(max_digits=5, decimal_places=0, default=0)
    gas_end = models.DecimalField(max_digits=5, decimal_places=0, default=0)
    gas_given = models.DecimalField(max_digits=5, decimal_places=0, default=0)
    shoulder = models.FloatField(default=0)
    count = models.DecimalField(default=1, max_digits=5, decimal_places=0)
    create_time = models.DateTimeField(auto_now=True)
    price = models.FloatField(default=0)
    

    class Meta:
        get_latest_by = 'race_date'
        ordering = ('race_date',)

    def __str__(self):
        return '%s' % self.id_race

    def get_absolute_url(self):
        return reverse('RaceUpdate', kwargs={'pk': self.pk})

    @classmethod
    def get_foreign_fields(cls):
        return [getattr(cls, f.name) for f in cls._meta.fields if isinstance(
            f, models.fields.related.ForeignKey)]

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
    def get_load_place(self):
        if not self.place_load:
            return self.supplier.address
        else:
            return self.place_load.address

    @property
    def get_unload_place(self):
        if not self.shipment:
            return self.customer.address
        else:
            return self.shipment.name

    @property
    def get_shipper(self):
        const = Constants.objects.get(pk=1)
        # реализация без посредника
        if self.car.mediator is None and (self.type_ship == self.TYPE[0][0]):
            return const.organization_unit_full + " " + const.address
        # реализация с посредником
        if self.car.mediator is not None and (
                self.type_ship == self.TYPE[0][0]):
            return const.organization_unit_full + " " + const.address
        # услуги без посредника, заказчик поставщик
        if self.car.mediator is None and(
                self.type_ship == self.TYPE[1][0]) and(
                self.order_type_race == self.ORDER[0][0]):
            return self.supplier.name + " " + self.supplier.address
        # услуги с посредником, заказчик поставщик
        if self.car.mediator is not None and(
                self.type_ship == self.TYPE[1][0]) and(
                self.order_type_race == self.ORDER[0][0]):
            return self.supplier.name + " " + self.supplier.address
        # услуги без посредника, заказчик покупатель
        if self.car.mediator is None and(
                self.type_ship == self.TYPE[1][0]) and(
                self.order_type_race == self.ORDER[1][1]):
            return self.customer.name + " " + self.customer.address
        # услуги с посредником, заказчик покупатель
        if self.car.mediator is not None and(
                self.type_ship == self.TYPE[1][0]) and(
                self.order_type_race == self.ORDER[1][1]):
            return self.customer.name + " " + self.customer.address

    @property
    def get_consignee(self):
        return self.customer.name + ", " + self.customer.address

    @property
    def get_car(self):
        return self.car.brand + " " + self.car.number + " " + \
               self.car.trailer.brand_trailer + " " + self.car.trailer.number

    @property
    def get_carrier(self):
        const = Constants.objects.get(pk=1)
        if self.car.mediator is not None and (
                self.type_ship != self.TYPE[1][0]):
            return self.car.mediator.name + " " + self.car.mediator.address
        else:
            return const.organization_unit_full + " " + const.address

            
class Abonent(models.Model):
    START, AUTH, PASS, READY, RACE, ACCEPTED, LOADING, LOADED, UNLOADING, UNLOADED, BAN = \
    'start', 'auth', 'pass', 'ready', 'race', 'accepted', 'loading', 'loaded', 'unloading', 'unloaded', 'ban'
    STATE = (
        (START, 'Начало'),
        (AUTH, 'Аутентификация'),
        (PASS, 'Запрос ключа'),
        (READY, 'Готов'),
        (RACE, 'Рейс'),
        (ACCEPTED, 'Принято'),
        (LOADING, 'Погрузка'),
        (LOADED, 'Загружен'),
        (UNLOADING, 'Разгрузка'),
        (UNLOADED, 'Разгружен'),
        (BAN, 'Заблокирован'),
    )
#    id_abonent = models.AutoField(primary_key=True)
    telegram_id = models.DecimalField(primary_key=True,
        unique=True, max_digits=12, decimal_places=0, max_length=10)
    telegram_nick = models.CharField(max_length=16, default='NoName', verbose_name='Никнейм')	
    secret = models.CharField(max_length=8, default='12345678', verbose_name='Секретный ключ')	
    auth_try = models.DecimalField(max_digits=5, decimal_places=0, default=0)
    active = models.BooleanField(default=True)
    admin = models.BooleanField(default=False)
    state = models.CharField(default=STATE[0], choices=STATE, max_length=25)
    last_seen = models.DateTimeField(null=True, blank=True)
    car = models.ForeignKey(Car, null=True, blank=True)
    race = models.ForeignKey(Race, null=True, blank=True)
    context = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return '{}:{}'.format(self.telegram_nick, self.telegram_id)
                                        
    @property
    def get_race_id(self):
        if self.race is not None:
            return self.race.pk
        else:
            return 0 
            
    def set_race(self, race_id=None):
        if race_id is not None:
            self.race = self.car.race_set.get(pk=race_id)
            
    def new_races(self):
        if self.car is not None:
            return self.car.race_set.filter(state=Race.CREATE, race_date__gte=timezone.now()-timedelta(days=3))
