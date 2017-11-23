# -*- coding:utf-8 -*-
from django import forms
from .models import Car

MONTHS = {
    1: 'jan', 2: 'feb', 3: 'mar', 4: 'apr',
    5: 'may', 6: 'jun', 7: 'jul', 8: 'aug',
    9: 'sep', 10: 'oct', 11: 'nov', 12: 'dec'
}


class CarForm(forms.Form):
    number = forms.CharField(label='Номер машины', max_length=10)
    pts = forms.CharField(label='PTS', max_length=10)


class SupplierForm(forms.Form):
    name = forms.CharField(label='Поставщик:', max_length=256)


class ProductForm(forms.Form):
    name = forms.CharField(label='Товар:', max_length=100)


class ShipmentForm(forms.Form):
    name = forms.CharField(label='Место разгрузки', max_length=100)


class MediatorForm(forms.Form):
    address = forms.CharField(label='Юр. адрес', max_length=256)


class CustomerForm(forms.Form):
    name = forms.CharField(label='Клиент', max_length=256)
    shipment = forms.ChoiceField(label='Место разгрузки')


class DriverForm(forms.Form):
    name = forms.CharField(label='Водитель', max_length=256)


class RaceForm(forms.Form):
    name_race = forms.CharField(label='Рейс', max_length=5)
    race_date = forms.DateInput()
    car = forms.ChoiceField()
    driver = forms.ChoiceField()
    type_ship = forms.BooleanField(label='Тип работы')
    supplier = forms.ChoiceField()
    customer = forms.ChoiceField()
    shipment = forms.ChoiceField()
    mediator = forms.ChoiceField()
    s_milage = forms.FloatField()
    e_milage = forms.FloatField()
    weight_load = forms.FloatField()
    weight_unload = forms.FloatField()
    comm = forms.Textarea()
