# -*- coding:utf-8 -*-
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, reverse
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
from .forms import MediatorForm
from .forms import ShipmentForm


def RaceView(req):
        date = timezone.now().date()
        current_race = Race.objects.all().filter(race_date=date)
        if req.method == 'POST' and req.POST['name'] == 'add':
            form = CarForm(req.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('Race'))
            else:
                return render(request=req, template_name='car.html', context={'form': form, 'current_race': current_race})
        else:
            form = RaceForm()
            return render(request=req, template_name='race.html', context={'form': form, 'current_race': current_race})


def CarView(req):
    qCar = Car.objects.all()
    if req.method == 'POST' and req.POST['name'] == 'add':
        form = CarForm(req.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('Car'))
    else:
        form = CarForm()
        return render(request=req, template_name='car.html', context={'form': form, 'qCar': qCar})

def TrailerView(req):
    qTrailer = Trailer.objects.all()
    if req.method == 'POST' and req.POST['name'] == 'add':
        form = TrailerForm(req.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('Trailer'))
    else:
        form = TrailerForm()
        return render(request=req, template_name='trailer.html', context={'form': form, 'qTrailer': qTrailer})

def DriverView(req):
    qDriver = Driver.objects.all()
    if req.method == 'POST' and req.POST['name'] == 'add':
        form = DriverForm(req.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('Driver'))
    else:
        form = DriverForm()
        return render(request=req, template_name='driver.html', context={'form': form, 'qDriver': qDriver})

def ProductView(req):
    qProduct = Product.objects.all()
    if req.method == 'POST' and req.POST['name'] == 'add':
        form = ProductForm(req.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('Product'))
    else:
        form = ProductForm()
        return render(request=req, template_name='product.html', context={'form': form, 'qProduct': qProduct})


def CustomerView(req):
    qCustomer = Customer.objects.all()
    if req.method == 'POST' and req.POST['name'] == 'add':
        form = CustomerForm(req.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('Customer'))
    else:
        form = CustomerForm()
        return render(request=req, template_name='customer.html', context={'form': form, 'qCustomer': qCustomer})


def SupplierView(req):
    qSupplier = Supplier.objects.all()
    if req.method == 'POST' and req.POST['name'] == 'add':
        form = Supplier(req.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('Supplier'))
    else:
        form = SupplierForm()
        return render(request=req, template_name='supplier.html', context={'form': form, 'qSupplier': qSupplier})


def MediatorView(req):
    qMediator= Mediator.objects.all()
    if req.method == 'POST' and req.POST['name'] == 'add':
        form = MediatorForm(req.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('Mediator'))
    else:
        form = MediatorForm()
        return render(request=req, template_name='mediator.html', context={'form': form, 'qMediator': qMediator})


def ShipmentView(req):
    qShipment= Shipment.objects.all()
    if req.method == 'POST' and req.POST['name'] == 'add':
        form = ShipmentForm(req.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('Shipment'))
    else:
        form = ShipmentForm()
        return render(request=req, template_name='shipment.html', context={'form': form, 'qShipment': qShipment})
