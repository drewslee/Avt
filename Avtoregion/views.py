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
from .forms import DriverForm
from .forms import ProductForm
from .forms import CustomerForm
from .forms import SupplierForm
from .forms import RaceForm
from .forms import TrailerForm


def index(req):
    date = timezone.now().date()
    current_race = Race.objects.all().filter(race_date=date)
    if current_race.count() != 0:
        return render(request=req, template_name='index.html', context={'current_race': current_race})
    else:
        return render(request=req, template_name='index.html')


def RaceView(req):
        date = timezone.now().date()
        current_race = Race.objects.all().filter(race_date=date)
        if req.method == 'POST':
            return render(request=req, template_name='catalog.html', context={'current_race': current_race})
        else:
            form = RaceForm()
            return render(request=req, template_name='catalog.html', context={'form': form, 'current_race': current_race})


def CarView(req):
    qCar = Car.objects.all()
    if req.method == 'POST':
        form = CarForm(req.POST)
        if form.is_valid():
            form.save()
            qCar = Car.objects.all()
            return render(request=req, template_name='catalog.html', context={'qCar': qCar})
    else:
        form = CarForm()
        return render(request=req, template_name='catalog.html', context={'form': form, 'qCar': qCar})


def DriverView(req):
    qDriver = Driver.objects.all()
    if req.method == 'POST':
        return render(request=req, template_name='index.html', context={'qDriver': qDriver})
    else:
        form = DriverForm()
        return render(request=req, template_name='index.html', context={'form': form})

def ProductView(req):
    qProduct = Product.objects.all()
    if req.method == 'POST':
        return render(request=req, template_name='index.html', context={'qProduct': qProduct})
    else:
        form = ProductForm()
        return render(request=req, template_name='index.html', context={'form': form})


def CustomerView(req):
    qCustomer = Customer.objects.all()
    if req.method == 'POST':
        return render(request=req, template_name='index.html', context={'qCustomer': qCustomer})
    else:
        form = CustomerForm()
        return render(request=req, template_name='index.html', context={'form': form})


def SupplierView(req):
    qSupplier = Supplier.objects.all()
    if req.method == 'POST':
        return render(request=req, template_name='index.html', context={'qSupplier': qSupplier})
    else:
        form = SupplierForm()
        return render(request=req, template_name='index.html', context={'form': form})


def catalog(req):
    pass


def add(req):
    if req.method == 'POST':
        pass

    #if form.is_valid():
    #    Car.objects.create(number=form.cleaned_data['number'], pts=form.cleaned_data['pts'])

