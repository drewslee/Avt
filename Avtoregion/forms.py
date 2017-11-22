# -*- coding:utf-8 -*-
from django import forms


class CarForm(forms.Form):
    number = forms.CharField(label='Номер машины', max_length=10)
    pts = forms.CharField(label='PTS', max_length=10)
