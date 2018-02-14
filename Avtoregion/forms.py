# -*- coding:utf-8 -*-

from django.forms import ModelForm, CharField, TextInput, PasswordInput
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.forms.widgets import SelectDateWidget
from django.forms import DateField, DateTimeField
from django.utils import timezone
from .models import *

MONTHS = {
    1: 'январь', 2: 'февраль', 3: 'март', 4: 'апрель',
    5: 'май', 6: 'июнь', 7: 'июль', 8: 'август',
    9: 'сентябрь', 10: 'октябрь', 11: 'ноябрь', 12: 'декабрь'
}


class CustomAuthForm(AuthenticationForm):
    username = UsernameField(
        max_length=254,
        widget=TextInput(attrs={'autofocus': True, 'class': 'form-control'}),
    )
    password = CharField(
        label=("Password"),
        strip=False,
        widget=PasswordInput(attrs={'class': 'form-control'}),
    )


class ConstantForm(ModelForm):
    class Meta:
        model = Constants
        fields = '__all__'
        labels = {'organization_unit_full': 'Название организации полностью',
                  'organization_unit_small': 'Короткое название организации',
                  'mechanic': 'Механик', 'dispatcher': 'Дистпечер', 'ogrn': 'ОГРН'}


class TrailerForm(ModelForm):
    class Meta:
        model = Trailer
        fields = ['number', 'brand_trailer', 'garage_number_trailer']
        labels = {'number': 'Прицеп', 'brand_trailer': 'Марка', 'garage_number_trailer': 'Гаражный номер'}


class CarForm(ModelForm):
    class Meta:
        model = Car
        fields = ['number', 'pts', 'trailer', 'mediator', 'brand', 'garage_number']
        labels = {'number': 'Номер машины', 'pts': 'ПТС', 'trailer': 'Прицеп', 'mediator': 'Посредник',
                  'brand': 'Марка', 'garage_number': 'Гаражный номер'}


class SupplierForm(ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'inn', 'address']
        labels = {'name': 'Поставщик', 'inn': 'ИНН', 'address': 'Адрес организации'}


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'units']
        labels = {'name': 'Название', 'fraction': 'Фракция', 'units': 'Единица измерения'}


class ShipmentForm(ModelForm):
    class Meta:
        model = Shipment
        fields = ['name']
        labels = {'name': 'Место разгрузки'}


class MediatorForm(ModelForm):
    class Meta:
        model = Mediator
        fields = ['name', 'address', 'inn', ]
        labels = {'address': 'Адрес организации', 'inn': 'ИНН', 'name': 'Название организации'}


class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'inn', 'address']
        labels = {'name': 'Клиент', 'inn': 'ИНН', 'address': 'Адрес организации'}


class DriverForm(ModelForm):
    date_med = DateField(widget=SelectDateWidget(), label='Дата мед. освидетельствования:')

    class Meta:
        model = Driver
        fields = ['name', 'personnel_number', 'driver_card', 'date_med']
        labels = {'name': 'Водитель:', 'personnel_number': 'Табельный номер',
                  'driver_card': 'Удостоверение'}


class RaceForm(ModelForm):
    race_date = DateTimeField(initial=timezone.now,
                              label='Дата выезда:')
    arrival_time = DateTimeField(initial=timezone.now, label='Дата приезда:')

    class Meta:
        model = Race
        fields = '__all__'
        labels = {
            'car': 'Машина',
            'driver': 'Водитель',
            'type_ship': 'Реализация',
            'supplier': 'Поставщик',
            'customer': 'Клиент',
            'shipment': 'Место разгрузки',
            'product': 'Груз',
            's_milage': 'Начало трeка',
            'e_milage': 'Конец трeка',
            'mediator': 'Посредник',
            'weight_unload': 'Разгружено',
            'weight_load': 'Загружено',
            'shoulder': 'Плечо',
            'comm': 'Комментарий',
            'state': 'Состояние',
            'gas_given': 'Горючего выдано на рейс',
            'gas_start': 'Горючего остаток на начало рейса',
            'gas_end': 'Горючего остаток на конец рейса',
        }
