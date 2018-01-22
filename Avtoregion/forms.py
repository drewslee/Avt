# -*- coding:utf-8 -*-

from django.forms import ModelForm, CharField, TextInput, PasswordInput
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.forms.widgets import SelectDateWidget
from django.forms import DateField
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


class TrailerForm(ModelForm):
    class Meta:
        model = Trailer
        fields = ['number']
        labels = {'number': 'Прицеп'}


class CarForm(ModelForm):
    class Meta:
        model = Car
        fields = ['number', 'pts', 'trailer', 'mediator']
        labels = {'number': 'Номер машины', 'pts': 'ПТС', 'trailer': 'Прицеп', 'mediator': 'Посредник'}


class SupplierForm(ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'inn']
        labels = {'name': 'Поставщик', 'inn': 'ИНН'}


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['name']
        labels = {'name': 'Груз'}


class ShipmentForm(ModelForm):
    class Meta:
        model = Shipment
        fields = ['name']
        labels = {'name': 'Место разгрузки'}


class MediatorForm(ModelForm):
    class Meta:
        model = Mediator
        fields = ['address', 'inn']
        labels = {'address': 'Адрес', 'inn': 'ИНН'}


class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'inn']
        labels = {'name': 'Клиент', 'inn': 'ИНН'}


class DriverForm(ModelForm):
    class Meta:
        model = Driver
        fields = ['name']
        labels = {'name': 'Водитель:'}


class RaceForm(ModelForm):
    race_date = DateField(widget=SelectDateWidget(), initial=timezone.now, label='Дата:')

    class Meta:
        model = Race
        fields = '__all__'
        labels = {
            'name_race': 'Номер рейса',
            'car': 'Машина',
            'driver': 'Водитель',
            'type_ship': 'Реализация',
            'supplier': 'Поставщик',
            'customer': 'Клиент',
            'shipment': 'Место разгрузки',
            'product': 'Груз',
            's_milage': 'Начало трeка',
            'e_milage': 'Конец трeка',
            'weight_unload': 'Разгружено',
            'weight_load': 'Загружено',
            'comm': 'Комментарий',
            'state': 'Состояние',
        }
