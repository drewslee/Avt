# -*- coding:utf-8 -*-
from django.db.models import fields
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.shortcuts import render, reverse
from django.contrib.auth.decorators import login_required
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
from django.db.models import Sum

@login_required
def RaceAll(req):
    if req.method == 'GET':
        qRace = Race.objects.all()
        return render(request=req, template_name='race.html', context={'qRace': qRace})


@login_required
def RaceView(req):
    if req.method == 'GET':
        if req.GET.get('input_date') is not None:
            date = req.GET.get('input_date')
        else:
            date = timezone.now().date()
        qRace = Race.objects.all().filter(race_date=date)
        return render(request=req, template_name='race.html', context={'qRace': qRace})


def CarView(req):
    qCar = Car.objects.all()
    if req.method == 'POST':
        form = CarForm(req.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('Car'))
    else:
        form = CarForm()
        return render(request=req, template_name='car.html', context={'form': form, 'qCar': qCar})


def TrailerView(req):
    qTrailer = Trailer.objects.all()
    if req.method == 'POST':
        form = TrailerForm(req.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('Trailer'))
    else:
        form = TrailerForm()
        return render(request=req, template_name='trailer.html', context={'form': form, 'qTrailer': qTrailer})


def DriverView(req):
    qDriver = Driver.objects.all()
    if req.method == 'POST':
        form = DriverForm(req.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('Driver'))
    else:
        form = DriverForm()
        return render(request=req, template_name='driver.html', context={'form': form, 'qDriver': qDriver})


def ProductView(req):
    qProduct = Product.objects.all()
    if req.method == 'POST':
        form = ProductForm(req.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('Product'))
    else:
        form = ProductForm()
        return render(request=req, template_name='product.html', context={'form': form, 'qProduct': qProduct})


def CustomerView(req):
    qCustomer = Customer.objects.all()
    if req.method == 'POST':
        form = CustomerForm(req.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('Customer'))
    else:
        form = CustomerForm()
        return render(request=req, template_name='customer.html', context={'form': form, 'qCustomer': qCustomer})

class CustomerViewList(ListView):
    model = Customer
    template_name = 'customer.html'
    context_object_name = 'qCustomer'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CustomerForm()
        return context


def SupplierView(req):
    qSupplier = Supplier.objects.all()
    if req.method == 'POST':
        form = SupplierForm(req.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('Supplier'))
    else:
        form = SupplierForm()
        return render(request=req, template_name='supplier.html', context={'form': form, 'qSupplier': qSupplier})


def MediatorView(req):
    qMediator = Mediator.objects.all()
    if req.method == 'POST':
        form = MediatorForm(req.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('Mediator'))
    else:
        form = MediatorForm()
        return render(request=req, template_name='mediator.html', context={'form': form, 'qMediator': qMediator})


def ShipmentView(req):
    qShipment = Shipment.objects.all()
    if req.method == 'POST':
        form = ShipmentForm(req.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('Shipment'))
    else:
        form = ShipmentForm()
        return render(request=req, template_name='shipment.html', context={'form': form, 'qShipment': qShipment})


class DriverUpdate(UpdateView):
    model = Driver
    success_url = '/Driver'
    form_class = DriverForm


class DriverDelete(DeleteView):
    model = Driver
    success_url = '/Driver'


class SupplierUpdate(UpdateView):
    model = Supplier
    success_url = '/Supplier'
    form_class = SupplierForm


class SupplierDelete(DeleteView):
    model = Supplier
    success_url = '/Supplier'


class CarUpdate(UpdateView):
    model = Car
    success_url = '/Car'
    form_class = CarForm


class CarDelete(DeleteView):
    model = Car
    success_url = '/Car'


class ProductUpdate(UpdateView):
    model = Product
    success_url = '/Product'
    form_class = ProductForm


class ProductDelete(DeleteView):
    model = Product
    success_url = '/Product'


class TrailerUpdate(UpdateView):
    model = Trailer
    success_url = '/Trailer'
    form_class = TrailerForm


class TrailerDelete(DeleteView):
    model = Trailer
    success_url = '/Trailer'


class ShipmentUpdate(UpdateView):
    model = Shipment
    success_url = '/Shipment'
    form_class = ShipmentForm


class ShipmentDelete(DeleteView):
    model = Shipment
    success_url = '/Shipment'


class MediatorUpdate(UpdateView):
    model = Mediator
    success_url = '/Mediator'
    form_class = MediatorForm


class MediatorDelete(DeleteView):
    model = Mediator
    success_url = '/Mediator'


class CustomerAdd(CreateView):
    model = Customer
    form_class = CustomerForm
    success_url = '/Customer'


class CustomerUpdate(UpdateView):
    model = Customer
    success_url = '/Customer'
    form_class = CustomerForm


class CustomerDelete(DeleteView):
    model = Customer
    success_url = '/Customer'


class RaceCreate(CreateView):
    model = Race
    form_class = RaceForm
    success_url = '/Race'


def RaceUpdate(req):
    if req.method == 'POST' and req.POST.get('update'):
        race_instance = Race.objects.get(pk=req.POST['pk'])
        form = RaceForm(instance=race_instance)
        return render(request=req, template_name='Avtoregion/race_form.html',
                      context={'form': form, 'pk': req.POST['pk']})
    elif req.method == 'POST' and req.POST.get('add'):
        race_instance = Race.objects.get(pk=req.POST['pk'])
        form = RaceForm(req.POST, instance=race_instance)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('Race'))


# class RaceUpdate(UpdateView):
#     model = Race
#     form_class = RaceForm
#     success_url = '/Race'
#     initial = {'name_race': '666'}
#
#     def get_object(self, queryset=None):
#         return get_object_or_404(self.model, pk=self.request.POST.get('pk'))
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         return context
#
#     def get_initial(self):
#         obj = self.get_object()
#         return super(RaceUpdate, self).get_initial()
#
#     def form_invalid(self, form):
#         print(form)
#         return self.render_to_response(self.get_context_data(**{'form': form}))



class RaceDelete(DeleteView):
    model = Race
    success_url = "/Race"

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.request.POST.get('pk'))


def AccumulateSup(req):
    qset = Supplier.objects.all()
    q_prod = Product.objects.all()
    if req.method == 'GET':
        return render(request=req, template_name='Avtoregion/accumulate_supplier.html',
                      context={'qset': qset, 'q_prod': q_prod})
    if req.method == 'POST':
        fields = [field.name for field in Race._meta.fields]
        fields.remove('weight_unload')
        q_resp = Race.objects.filter(supplier__inn__exact=req.POST.get('supplier'),
                                     race_date__range=[req.POST.get('from'), req.POST.get('to')],
                                     product__name__exact=req.POST.get('product')).values(*fields)
        q_weight = q_resp.aggregate(Sum('weight_load'))
        for obj in q_resp:
            obj['car'] = Car.objects.get(id_car=obj.get('car')).number
            obj['product'] = Product.objects.get(id_product=obj.get('product')).name

        return render(request=req, template_name='Avtoregion/account.html',
                      context={'q_resp': q_resp, 'q_weight': q_weight})


class Accumulate(ListView):
    context_object_name = 'qset'
    template_name = 'Avtoregion/accumulate_customer.html'
    model = Customer


def AccumulateCus(req):
    qset = Customer.objects.all()
    q_prod = Product.objects.all()
    if req.method == 'GET':
        return render(request=req, template_name='Avtoregion/accumulate_customer.html', context={'qset': qset, 'q_prod': q_prod})
    if req.method == 'POST':
        fields = [field.name for field in Race._meta.fields]
        fields.remove('weight_load')
        q_resp = Race.objects.filter(customer__inn__exact=req.POST.get('customer'),
                                     race_date__range=[req.POST.get('from'), req.POST.get('to')],
                                     product__name__exact=req.POST.get('product')).values(*fields)
        q_weight = q_resp.aggregate(Sum('weight_unload'))
        print(q_weight)
        for obj in q_resp:
            obj['car'] = Car.objects.get(id_car=obj.get('car')).number
            obj['product'] = Product.objects.get(id_product=obj.get('product')).name

        return render(request=req, template_name='Avtoregion/account.html',
                      context={'q_resp': q_resp, 'q_weight': q_weight})


def AccumulateCar(req):
    qset = Car.objects.all()
    if req.method == 'GET':
        return render(request=req, template_name='Avtoregion/accumulate_car.html', context={'qset': qset})
    if req.method == 'POST':
        q_resp = Race.objects.filter(car__number__exact=req.POST.get('radio'),
                                     race_date__range=[req.POST.get('from'), req.POST.get('to')])
        return render(request=req, template_name='Avtoregion/account_car.html',
                      context={'q_resp': q_resp})


def AccumulateDriver(req):
    qset = Driver.objects.all()
    if req.method == 'GET':
        return render(request=req, template_name='Avtoregion/accumulate_driver.html', context={'qset': qset})
    if req.method == 'POST':
        q_resp = Race.objects.filter(driver__name__exact=req.POST.get('radio'),
                                     race_date__range=[req.POST.get('from'), req.POST.get('to')])
        return render(request=req, template_name='Avtoregion/account_driver.html', context={'q_resp': q_resp})
