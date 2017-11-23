# -*- coding:utf-8 -*-
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from .models import Car
from .models import Driver
from .models import Customer
from .models import Product
from .models import Shipment
from .models import Milage
from .models import Supplier
from .models import Trailer
from .models import Race
from .models import Mediator
from .forms import CarForm


def index(req):
    current_race = Race.objects.all().filter(race_date=timezone.now().date())
    if current_race.count() != 0:
        return render(request=req, template_name='index.html', context={'current_race': current_race})
    else:
        return render(request=req, template_name='index.html')


def catalog(req):
    return render(request=req, template_name='index.html')


def car(req):
    if req.method == 'POST':
        form = CarForm(req.POST)
        if form.is_valid():
            Car.objects.create(number=form.cleaned_data['number'], pts=form.cleaned_data['pts'])
            return HttpResponseRedirect(redirect_to='/catalog/')
    else:
        form = CarForm()
    return render(request=req, template_name='catalog.html', context={'form': form})
