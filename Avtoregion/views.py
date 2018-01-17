# -*- coding:utf-8 -*-
from django.db.models import fields
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.utils import timezone
from django.db.models import Q
from .models import Car
from .models import Driver
from .models import Customer
from .models import Product
from .models import Shipment
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
import xlwt, os
from django.conf import settings as djangoSettings

class RaceAllList(LoginRequiredMixin, ListView):
    model = Race
    template_name = 'race.html'
    context_object_name = 'qRace'
    paginate_by = 5
    queryset = Race.objects.order_by('id_race')


class RaceViewList(LoginRequiredMixin, ListView):
    model = Race
    template_name = 'race_date.html'
    context_object_name = 'qRace'

    def get_queryset(self):
        if self.request.GET.get('input_date_from') is None or self.request.GET.get('input_date_to') is None:
            queryset = Race.objects.filter(race_date__range=[timezone.now().date(), timezone.now().date()])
        else:
            queryset = Race.objects.filter(race_date__range=[self.request.GET.get('input_date_from'),
                                                             self.request.GET.get('input_date_to')])
        return queryset


class RaceCreate(SuccessMessageMixin, PermissionRequiredMixin, CreateView):
    model = Race
    form_class = RaceForm
    success_url = reverse_lazy('RaceCreate')
    success_message = "Рейс %(name_race)s создан успешно"
    permission_required = ('races.add_race',)


class RaceUpdate(SuccessMessageMixin, PermissionRequiredMixin, UpdateView):
    model = Race
    form_class = RaceForm
    success_message = "Рейс %(name_race)s обновлён успешно"
    permission_required = ('races.update_race',)


class RaceDelete(SuccessMessageMixin, PermissionRequiredMixin, DeleteView):
    model = Race
    success_url = '/Race'
    success_message = "Рейс %(name_race)s удалён"
    permission_required = ('races.delete_race',)


#    def get_object(self, queryset=None):
#        return self.model.objects.get(pk=self.request.POST.get('pk'))


class CarViewList(LoginRequiredMixin, ListView):
    model = Car
    template_name = 'car.html'
    context_object_name = 'qCar'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CarForm()
        return context


class TrailerViewList(LoginRequiredMixin, ListView):
    model = Trailer
    template_name = 'trailer.html'
    context_object_name = 'qTrailer'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = TrailerForm()
        return context


class DriverViewList(LoginRequiredMixin, ListView):
    model = Driver
    template_name = 'driver.html'
    context_object_name = 'qDriver'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = DriverForm()
        return context


class ProductViewList(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'product.html'
    context_object_name = 'qProduct'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ProductForm()
        return context


class CustomerViewList(LoginRequiredMixin, ListView):
    model = Customer
    template_name = 'customer.html'
    context_object_name = 'qCustomer'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CustomerForm()
        return context


class SupplierViewList(LoginRequiredMixin, ListView):
    model = Supplier
    template_name = 'supplier.html'
    context_object_name = 'qSupplier'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SupplierForm()
        return context


class ShipmentViewList(LoginRequiredMixin, ListView):
    model = Shipment
    template_name = 'shipment.html'
    context_object_name = 'qShipment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ShipmentForm()
        return context


class MediatorViewList(LoginRequiredMixin, ListView):
    model = Mediator
    template_name = 'mediator.html'
    context_object_name = 'qMediator'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = MediatorForm()
        return context


class DriverUpdate(PermissionRequiredMixin, UpdateView):
    model = Driver
    success_url = reverse_lazy('DriverUpdate')
    form_class = DriverForm
    permission_required = ('drivers.update_driver',)


class DriverDelete(PermissionRequiredMixin, DeleteView):
    model = Driver
    success_url = reverse_lazy('Driver')
    permission_required = ('drivers.delete_driver',)


class SupplierUpdate(PermissionRequiredMixin, UpdateView):
    model = Supplier
    success_url = reverse_lazy('SupplierUpdate')
    form_class = SupplierForm
    permission_required = ('suppliers.update_supplier',)


class SupplierDelete(PermissionRequiredMixin, DeleteView):
    model = Supplier
    success_url = reverse_lazy('Supplier')
    permission_required = ('suppliers.delete_supplier',)


class CarUpdate(PermissionRequiredMixin, UpdateView):
    model = Car
    success_url = reverse_lazy('CarUpdate')
    form_class = CarForm
    permission_required = ('cars.update_car',)


class CarDelete(PermissionRequiredMixin, DeleteView):
    model = Car
    success_url = reverse_lazy('Car')
    permission_required = ('cars.delete_cars',)


class ProductUpdate(PermissionRequiredMixin, UpdateView):
    model = Product
    success_url = reverse_lazy('ProductUpdate')
    form_class = ProductForm
    permission_required = ('products.update_product',)


class ProductDelete(PermissionRequiredMixin, DeleteView):
    model = Product
    success_url = reverse_lazy('Product')
    permission_required = ('products.delete_product',)


class TrailerUpdate(PermissionRequiredMixin, UpdateView):
    model = Trailer
    success_url = reverse_lazy('TrailerUpdate')
    form_class = TrailerForm
    permission_required = ('trailers.update_trailer',)


class TrailerDelete(PermissionRequiredMixin, DeleteView):
    model = Trailer
    success_url = reverse_lazy('Trailer')
    permission_required = ('trailers.delete_trailer',)


class ShipmentUpdate(PermissionRequiredMixin, UpdateView):
    model = Shipment
    success_url = reverse_lazy('ShipmentUpdate')
    form_class = ShipmentForm
    permission_required = ('shipments.update_shipment',)


class ShipmentDelete(PermissionRequiredMixin, DeleteView):
    model = Shipment
    success_url = reverse_lazy('Shipment')
    permission_required = ('shipments.delete_shipment',)


class MediatorUpdate(PermissionRequiredMixin, UpdateView):
    model = Mediator
    success_url = reverse_lazy('MediatorUpdate')
    form_class = MediatorForm
    permission_required = ('mediators.update_mediator',)


class MediatorDelete(PermissionRequiredMixin, DeleteView):
    model = Mediator
    success_url = reverse_lazy('Mediator')
    permission_required = ('mediators.delete_mediator',)


class CustomerAdd(PermissionRequiredMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    success_url = reverse_lazy('CustomerAdd')
    permission_required = ('customers.add_customer',)


class CustomerUpdate(PermissionRequiredMixin, UpdateView):
    model = Customer
    success_url = reverse_lazy('CustomerUpdate')
    form_class = CustomerForm
    permission_required = ('customers.update_customer',)


class CustomerDelete(PermissionRequiredMixin, DeleteView):
    model = Customer
    success_url = reverse_lazy('Customer')
    permission_required = ('customers.delete_customer',)


def accumulate_sup(req):
    qset = Supplier.objects.all()
    q_prod = Product.objects.all()
    if req.method == 'GET':
        return render(request=req, template_name='Avtoregion/accumulate_supplier.html',
                      context={'qset': qset, 'q_prod': q_prod})
    if req.method == 'POST':
        fields = [field.name for field in Race._meta.fields]
        fields.remove('weight_unload')
        query = Q(supplier__id_supplier=req.POST.get('supplier'),
                  race_date__range=[req.POST.get('from'), req.POST.get('to')]
                  )
        if req.POST.get('product') is not None:
            prod = req.POST.getlist('product')
            for v in prod:
                query.add(Q(product__name=v), Q.OR)
            q_resp = Race.objects.filter(query).order_by('product').filter(weight_load__gt=0).values(*fields)
        else:
            q_resp = Race.objects.filter(query).filter(weight_load__gt=0).values(*fields)
        sum_products = []
        for obj in q_resp:
            obj['car'] = Car.objects.get(id_car=obj.get('car')).number
            obj['product'] = Product.objects.get(id_product=obj.get('product')).name
            sum_products.append([obj.get('product'), obj.get('weight_load')])
        i = 0
        while True:
            try:
                if sum_products[i][0] == sum_products[i + 1][0]:
                    sum_products[i][1] += sum_products[i + 1][1]
                    del sum_products[i + 1]
                else:
                    i += 1
            except IndexError:
                break
        q_weight = q_resp.aggregate(Sum('weight_load'))
        filename = save_excel('supplier.xls', )

        return render(request=req, template_name='Avtoregion/account.html',
                      context={'q_resp': q_resp, 'q_weight': q_weight, 'filename': filename})


class Accumulate(LoginRequiredMixin, ListView):
    context_object_name = 'qset'
    template_name = 'Avtoregion/accumulate_customer.html'
    model = Customer


def accumulate_cus(req):
    qset = Customer.objects.all()
    q_prod = Product.objects.all()
    if req.method == 'GET':
        return render(request=req, template_name='Avtoregion/accumulate_customer.html',
                      context={'qset': qset, 'q_prod': q_prod})
    if req.method == 'POST':
        fields = [field.name for field in Race._meta.fields]
        fields.remove('weight_load')
        query = Q(customer__id_customer__exact=req.POST.get('customer'),
                  race_date__range=[req.POST.get('from'), req.POST.get('to')]
                  )
        if req.POST.get('product') is not None:
            prod = req.POST.getlist('product')
            for v in prod:
                query.add(Q(product__name=v), Q.OR)
            q_resp = Race.objects.filter(query).order_by('product').filter(weight_unload__gt=0).values(*fields)
        else:
            q_resp = Race.objects.filter(query).filter(weight_unload__gt=0).values(*fields)

        for obj in q_resp:
            obj['car'] = Car.objects.get(id_car=obj.get('car')).number
            obj['product'] = Product.objects.get(id_product=obj.get('product')).name
        q_weight = q_resp.aggregate(Sum('weight_unload'))
        return render(request=req, template_name='Avtoregion/account.html',
                      context={'q_resp': q_resp, 'q_weight': q_weight})


def accumulate_car(req):
    qset = Car.objects.all()
    if req.method == 'GET':
        return render(request=req, template_name='Avtoregion/accumulate_car.html', context={'qset': qset})
    if req.method == 'POST':
        q_resp = Race.objects.filter(car__number__exact=req.POST.get('radio'),
                                     race_date__range=[req.POST.get('from'), req.POST.get('to')])
        return render(request=req, template_name='Avtoregion/account_car.html',
                      context={'q_resp': q_resp})


def accumulate_driver(req):
    qset = Driver.objects.all()
    if req.method == 'GET':
        return render(request=req, template_name='Avtoregion/accumulate_driver.html', context={'qset': qset})
    if req.method == 'POST':
        q_resp = Race.objects.filter(driver__name__exact=req.POST.get('radio'),
                                     race_date__range=[req.POST.get('from'), req.POST.get('to')])
        return render(request=req, template_name='Avtoregion/account_driver.html', context={'q_resp': q_resp})


def accumulate_mediator(req):
    pass


def save_excel(filename, values_list, *col):

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('List1')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True


    for col_num in range(len(col)):
        ws.write(row_num, col_num, col[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = values_list('race_date', 'car_id__number', 'weight_load', 'product_id__name')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
    path_for_save = os.path.join(djangoSettings.BASE_DIR, 'static', filename)
    wb.save(filename_or_stream=path_for_save)
    return filename
