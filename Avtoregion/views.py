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


def index(req):
    current_race = Race.objects.all().filter(race_date=timezone.now().date())
    if current_race.count() != 0:
        return render(request=req, template_name='index.html', context={'current_race': current_race})
    else:
        return render(request=req, template_name='index.html')


def catalog(req):
    if req.method == 'POST':
        if 'Car' in req.POST and req.POST['Car'] == 'get':
            qCar = Car.objects.all()
            if qCar.count() != 0:
                return render(request=req, template_name='index.html', context={'qCar': qCar})
            else:
                form = CarForm()
                return render(request=req, template_name='index.html', context={'form': form})
        if 'Driver' in req.POST and req.POST['Driver'] == 'get':
            qDriver = Driver.objects.all()
            if qDriver.count() != 0:
                return render(request=req, template_name='index.html', context={'qDriver': qDriver})
            else:
                form = DriverForm()
                return render(request=req, template_name='index.html', context={'form': form})
        if 'Product' in req.POST and req.POST['Product'] == 'get':
            qProduct = Product.objects.all()
            if qProduct.count() != 0:
                return render(request=req, template_name='index.html', context={'qProduct': qProduct})
            else:
                form = ProductForm()
                return render(request=req, template_name='index.html', context={'form': form})
        if 'Customer' in req.POST and req.POST['Customer'] == 'get':
            qCustomer = Customer.objects.all()
            if qCustomer.count() != 0:
                return render(request=req, template_name='index.html', context={'qCustomer': qCustomer})
            else:
                form = CustomerForm()
                return render(request=req, template_name='index.html', context={'form': form})

        if 'Supplier' in req.POST and req.POST['Supplier'] == 'get':
            qSupplier = Supplier.objects.all()
            if qSupplier.count() != 0:
                return render(request=req, template_name='index.html', context={'qSupplier': qSupplier})
            else:
                form = SupplierForm()
                return render(request=req, template_name='index.html', context={'form': form})
def add(req):
    if req.method == 'POST':
        pass

    #if form.is_valid():
    #    Car.objects.create(number=form.cleaned_data['number'], pts=form.cleaned_data['pts'])

