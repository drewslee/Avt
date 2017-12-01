# -*- coding:utf-8 -*-

from django.forms import ModelForm
from django.contrib.admin.widgets import AdminDateWidget
from django.forms.widgets import SelectDateWidget
from .models import *

MONTHS = {
    1: 'январь', 2: 'февраль', 3: 'март', 4: 'апрель',
    5: 'май', 6: 'июнь', 7: 'июль', 8: 'август',
    9: 'сентябрь', 10: 'октябрь', 11: 'ноябрь', 12: 'декабрь'
}


class TrailerForm(ModelForm):
    class Meta:
        model = Trailer
        fields = ['number']


class CarForm(ModelForm):
    class Meta:
        model = Car
        fields = ['number', 'pts', 'trailer']


class SupplierForm(ModelForm):
    class Meta:
        model = Supplier
        fields = ['name']


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['name']


class ShipmentForm(ModelForm):
    class Meta:
        model = Shipment
        fields = ['name']


class MediatorForm(ModelForm):
    class Meta:
        model = Mediator
        fields = ['address']


class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = ['name']


class DriverForm(ModelForm):
    class Meta:
        model = Driver
        fields = ['name']


class RaceForm(ModelForm):
    class Meta:
        model = Race
        fields = '__all__'
        labels = {
                  'name_race': 'Номер рейса',
                  'race_date': 'Дата рейса',
                  'car': 'Машина',
                  'driver': 'Водитель',
                  'type_ship': 'Реализация',
                  'supplier': 'Поставщик',
                  'customer': 'Клиент',
                  'shipment': 'Место разгрузки',
                  'product': 'Груз',
                  'mediator': 'Посредник',
                  's_milage': 'Начало трeка',
                  'e_milage': 'Конец трeка',
                  'weight_unload': 'Разгружено',
                  'weight_load': 'Загружено',
                  'comm': 'Комментарий',
                  'state': 'Состояние',
        }
        widgets = {'race_date': SelectDateWidget(months=MONTHS)}
