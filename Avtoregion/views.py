# -*- coding:utf-8 -*-
import os
import xlwt
import json
import shutil
import tempfile
from datetime import timedelta
from django.http.response import HttpResponseRedirect, Http404, HttpResponse, HttpResponseServerError
from django.conf import settings as djangoSettings
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormMixin, View
from django.views.generic.list import ListView
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.messages import constants as messages_constants

from .forms import CarForm
from .forms import CustomAuthForm
from .forms import CustomerForm
from .forms import DriverForm
from .forms import MediatorForm
from .forms import ProductForm
from .forms import RaceForm
from .forms import ShipmentForm
from .forms import SupplierForm
from .forms import TrailerForm
from .forms import ConstantForm
from .forms import UnitsForm
from .models import Car
from .models import Customer
from .models import Driver
from .models import Mediator
from .models import Product
from .models import Race
from .models import Units
from .models import Shipment
from .models import Supplier
from .models import Trailer
from .models import Constants


class LoginViewMix(LoginView):
    form_class = CustomAuthForm


class ConstantsViewList(PermissionRequiredMixin, FormMixin, ListView):
    model = Constants
    template_name = 'Avtoregion/update_form.html'
    permission_required = ('constants.update_constants',)
    context_object_name = 'qConstants'

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        cxt = super(ListView, self).get_context_data(**kwargs)
        cnst, created = Constants.objects.get_or_create(pk=1)
        cxt['form'] = ConstantForm(instance=cnst)
        return cxt

    def post(self, *args, **kwargs):
        kwargs.update(self.request.POST)
        kwargs.pop('csrfmiddlewaretoken')
        for k, v in kwargs.items():
            kwargs[k] = v[0]
        kwargs['id'] = 1
        self.model.objects.update(**kwargs)
        return HttpResponseRedirect(redirect_to='Constants')


class RaceViewList(LoginRequiredMixin, ListView):
    model = Race
    template_name = 'race.html'
    context_object_name = 'qRace'

    def get_queryset(self):
        if self.request.GET.get('daterange') is None:
            end_date = Race.objects.latest().race_date
            start_date = end_date - timedelta(weeks=1)
            queryset = Race.objects.filter(race_date__range=[start_date, end_date]).order_by(
                'race_date')
        else:
            start_date, end_date = date_to_str(self.request.GET.get('daterange'))
            queryset = Race.objects.filter(race_date__range=[start_date, end_date]).order_by('race_date')
        return queryset

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['select_state'] = (x[1] for x in self.model.STATE)
        if self.request.GET.get('daterange') is not None:
            start_date, end_date = date_to_str(self.request.GET.get('daterange'))
            ctx['start_date'] = start_date
            ctx['end_date'] = end_date
        else:
            end_date = Race.objects.latest().race_date
            start_date = end_date - timedelta(weeks=1)
            ctx['start_date'] = str(start_date.strftime('%Y-%m-%d'))
            ctx['end_date'] = str(end_date.strftime('%Y-%m-%d'))
        return ctx


class RaceCreate(SuccessMessageMixin, PermissionRequiredMixin, CreateView):
    model = Race
    form_class = RaceForm
    template_name = 'Avtoregion/race_form.html'
    success_url = reverse_lazy('RaceCreate')
    success_message = "Рейс создан успешно"
    permission_required = ('races.add_race',)


class RaceUpdate(SuccessMessageMixin, PermissionRequiredMixin, UpdateView):
    model = Race
    form_class = RaceForm
    template_name = 'Avtoregion/update_form.html'
    success_url = reverse_lazy('Race')
    success_message = "Рейс обновлён успешно"
    permission_required = ('races.update_race',)


class RaceDelete(SuccessMessageMixin, PermissionRequiredMixin, DeleteView):
    model = Race
    success_url = '/Race'
    success_message = "Рейс удалён"
    permission_required = ('races.delete_race',)

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.request.POST.get('pk'))


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


class UnitsViewList(LoginRequiredMixin, ListView):
    model = Units
    template_name = 'units.html'
    context_object_name = 'qUnits'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = UnitsForm()
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


class DriverAdd(PermissionRequiredMixin, CreateView):
    model = Driver
    success_url = reverse_lazy('DriverList')
    form_class = DriverForm
    permission_required = ('drivers.add_driver',)


class DriverUpdate(PermissionRequiredMixin, UpdateView):
    model = Driver
    success_url = reverse_lazy('DriverList')
    form_class = DriverForm
    permission_required = ('drivers.update_driver',)


class DriverDelete(PermissionRequiredMixin, DeleteView):
    model = Driver
    success_url = reverse_lazy('DriverList')
    permission_required = ('drivers.delete_driver',)

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.request.POST.get('pk'))


class SupplierAdd(PermissionRequiredMixin, CreateView):
    model = Supplier
    success_url = reverse_lazy('SupplierList')
    form_class = SupplierForm
    permission_required = ('suppliers.add_supplier',)


class SupplierUpdate(PermissionRequiredMixin, UpdateView):
    model = Supplier
    success_url = reverse_lazy('SupplierList')
    form_class = SupplierForm
    permission_required = ('suppliers.update_supplier',)


class SupplierDelete(PermissionRequiredMixin, DeleteView):
    model = Supplier
    success_url = reverse_lazy('SupplierList')
    permission_required = ('suppliers.delete_supplier',)

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.request.POST.get('pk'))


class UnitAdd(PermissionRequiredMixin, CreateView):
    model = Units
    success_url = reverse_lazy('UnitList')
    form_class = UnitsForm
    permission_required = ('units.add_car',)


class UnitUpdate(PermissionRequiredMixin, UpdateView):
    model = Units
    success_url = reverse_lazy('UnitList')
    form_class = UnitsForm
    permission_required = ('units.update_car',)


class UnitDelete(PermissionRequiredMixin, DeleteView):
    model = Units
    success_url = reverse_lazy('UnitList')
    permission_required = ('units.delete_supplier',)

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.request.POST.get('pk'))


class CarAdd(PermissionRequiredMixin, CreateView):
    model = Car
    success_url = reverse_lazy('CarList')
    form_class = CarForm
    permission_required = ('cars.add_car',)


class CarUpdate(PermissionRequiredMixin, UpdateView):
    model = Car
    success_url = reverse_lazy('CarList')
    form_class = CarForm
    permission_required = ('cars.update_car',)


class CarDelete(PermissionRequiredMixin, DeleteView):
    model = Car
    success_url = reverse_lazy('CarList')
    permission_required = ('cars.delete_cars',)

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.request.POST.get('pk'))


class ProductAdd(PermissionRequiredMixin, CreateView):
    model = Product
    success_url = reverse_lazy('ProductList')
    form_class = ProductForm
    permission_required = ('products.add_product',)


class ProductUpdate(PermissionRequiredMixin, UpdateView):
    model = Product
    success_url = reverse_lazy('ProductList')
    form_class = ProductForm
    permission_required = ('products.update_product',)


class ProductDelete(PermissionRequiredMixin, DeleteView):
    model = Product
    success_url = reverse_lazy('ProductList')
    permission_required = ('products.delete_product',)

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.request.POST.get('pk'))


class TrailerAdd(PermissionRequiredMixin, CreateView):
    model = Trailer
    success_url = reverse_lazy('TrailerList')
    form_class = TrailerForm
    permission_required = ('trailers.add_trailer',)


class TrailerUpdate(PermissionRequiredMixin, UpdateView):
    model = Trailer
    success_url = reverse_lazy('TrailerList')
    form_class = TrailerForm
    permission_required = ('trailers.update_trailer',)


class TrailerDelete(PermissionRequiredMixin, DeleteView):
    model = Trailer
    success_url = reverse_lazy('TrailerList')
    permission_required = ('trailers.delete_trailer',)

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.request.POST.get('pk'))


class ShipmentAdd(PermissionRequiredMixin, CreateView):
    model = Shipment
    success_url = reverse_lazy('ShipmentList')
    form_class = ShipmentForm
    permission_required = ('shipments.add_shipment',)


class ShipmentUpdate(PermissionRequiredMixin, UpdateView):
    model = Shipment
    success_url = reverse_lazy('ShipmentList')
    form_class = ShipmentForm
    permission_required = ('shipments.update_shipment',)


class ShipmentDelete(PermissionRequiredMixin, DeleteView):
    model = Shipment
    success_url = reverse_lazy('ShipmentList')
    permission_required = ('shipments.delete_shipment',)

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.request.POST.get('pk'))


class MediatorAdd(PermissionRequiredMixin, CreateView):
    model = Mediator
    success_url = reverse_lazy('MediatorList')
    form_class = MediatorForm
    permission_required = ('mediators.add_mediator',)


class MediatorUpdate(PermissionRequiredMixin, UpdateView):
    model = Mediator
    success_url = reverse_lazy('MediatorList')
    form_class = MediatorForm
    permission_required = ('mediators.update_mediator',)


class MediatorDelete(PermissionRequiredMixin, DeleteView):
    model = Mediator
    success_url = reverse_lazy('MediatorList')
    permission_required = ('mediators.delete_mediator',)

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.request.POST.get('pk'))


class CustomerAdd(PermissionRequiredMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    success_url = reverse_lazy('CustomerList')
    permission_required = ('customers.add_customer',)


class CustomerUpdate(PermissionRequiredMixin, UpdateView):
    model = Customer
    success_url = reverse_lazy('CustomerList')
    form_class = CustomerForm
    permission_required = ('customers.update_customer',)


class CustomerDelete(PermissionRequiredMixin, DeleteView):
    model = Customer
    success_url = reverse_lazy('CustomerList')
    permission_required = ('customers.delete_customer',)

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.request.POST.get('pk'))


def accumulate_sup(req):
    qset = Supplier.objects.all()
    q_prod = Product.objects.all()
    if req.method == 'GET':
        return render(request=req, template_name='Avtoregion/accumulate_supplier.html',
                      context={'qset': qset, 'q_prod': q_prod})
    if req.method == 'POST':
        start_date, end_date = date_to_str(req.POST['daterange'])
        query = Q(supplier__id_supplier__exact=req.POST.get('supplier'),
                  race_date__range=[start_date, end_date]
                  )
        if req.POST.get('product') is not None:
            prod = req.POST.getlist('product')
            if len(prod) == 1:
                query.add(Q(product__name=prod[0]), Q.AND)
            else:
                for v in prod:
                    query.add(Q(product__name=v), Q.OR)
            q_resp = Race.objects.filter(query).order_by('product').filter(weight_load__gt=0)
        else:
            q_resp = Race.objects.filter(query).order_by('product').filter(weight_load__gt=0)
        q_weight = q_resp.aggregate(Sum('weight_load'))

        return render(request=req, template_name='Avtoregion/account.html',
                      context={'q_resp': q_resp, 'q_weight': q_weight})


class Accumulate(LoginRequiredMixin, ListView):
    context_object_name = 'qset'
    template_name = 'Avtoregion/accumulate_customer.html'
    model = Customer


def accumulate_cus(req):
    qset = Customer.objects.all()
    q_prod = Product.objects.all()
    if req.method == 'GET':
        print(req.GET)
        return render(request=req, template_name='Avtoregion/accumulate_customer.html',
                      context={'qset': qset, 'q_prod': q_prod})
    if req.method == 'POST':
        start_date, end_date = date_to_str(req.POST['daterange'])
        query = Q(customer__id_customer__exact=req.POST.get('customer'),
                  race_date__range=[start_date, end_date]
                  )
        if req.POST.get('product') is not None:
            prod = req.POST.getlist('product')
            if len(prod) == 1:
                query.add(Q(product__name=prod[0]), Q.AND)
            else:
                for v in prod:
                    query.add(Q(product__name=v), Q.OR)
            q_resp = Race.objects.filter(query).filter(weight_unload__gt=0)
        else:
            q_resp = Race.objects.filter(query).filter(weight_unload__gt=0)

        q_weight = q_resp.aggregate(Sum('weight_unload'))
        return render(request=req, template_name='Avtoregion/account.html',
                      context={'q_resp': q_resp, 'q_weight': q_weight})


class CarResponce(View):
    def get(self, *args, **kwargs):
        qset = Car.objects.all()
        return render(request=self.request, template_name='Avtoregion/accumulate_car.html', context={'qset': qset})

    def post(self, *args, **kwargs):
        start_date, end_date = date_to_str(self.request.POST['daterange'])
        q_resp = Race.objects.filter(car__number__exact=self.request.POST.get('car'),
                                     race_date__range=[start_date, end_date])
        return render(request=self.request, template_name='Avtoregion/account_car.html',
                      context={'q_resp': q_resp})


class DriverResponce(View):
    def get(self, *args, **kwargs):
        qset = Driver.objects.all()
        return render(request=self.request, template_name='Avtoregion/accumulate_driver.html', context={'qset': qset})

    def post(self, *args, **kwargs):
        start_date, end_date = date_to_str(self.request.POST['daterange'])
        q_resp = Race.objects.filter(driver__name__exact=self.request.POST.get('driver'),
                                     race_date__range=[start_date, end_date])
        return render(request=self.request, template_name='Avtoregion/account_driver.html',
                      context={'q_resp': q_resp})


def accumulate_mediator(req):
    pass


def save_excel(filename, values_list, col):
    filename = filename + (timezone.datetime.now().strftime('%y_%m_%d_%H_%M_%S')) + '.xls'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('List1')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    font_style.font.name = 'Times New Roman'


    for col_num in range(len(col)):
        ws.write(row_num, col_num, col[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    font_style.font.name = 'Times New Roman'
    for row in values_list:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)

    path_for_save = os.path.join(djangoSettings.BASE_DIR, 'static', 'temp', filename)
    wb.save(filename_or_stream=path_for_save)
    return '/'.join(['temp', filename])


def waybill_render(race_id):
    static_root = os.path.join(djangoSettings.BASE_DIR, 'static')
    const = Constants.objects.get(id=1)
    race = Race.objects.get(id_race=int(race_id))
    buf = render_to_string('sharedStrings.xml', {'race': race, 'const': const})
    filename = 'waybill_' + str(race_id) + '_' + (timezone.datetime.now().strftime('%y_%m_%d_%H_%M_%S'))
    with tempfile.TemporaryDirectory() as tmpdir:
        way = os.path.join(tmpdir, 'way')
        shutil.copytree(os.path.join(static_root, 'way'), way)
        with open(os.path.join(way, 'xl', 'sharedStrings.xml',), 'w', newline='\r\n') as f:
            f.write(buf)
        shutil.make_archive(os.path.join(static_root, 'temp', filename), 'zip', way, '.')
    os.rename(os.path.join(static_root, 'temp', filename + '.zip'), os.path.join(static_root, 'temp', filename + '.xlsx'))
    return '/'.join(['temp', filename + '.xlsx'])


def waybill(req):
    qset = Car.objects.all()
    if req.method == 'GET':
        return render(request=req, template_name='Avtoregion/waybill.html', context={'qset': qset})
    if req.method == 'POST':
        start_date, end_date = date_to_str(req.POST['daterange'])
        q_resp = Race.objects.filter(car__number__exact=req.POST.get('car'),
                                     race_date__range=[start_date, end_date])
        urls = []
        idlist = q_resp.values_list('id_race')
        for i in idlist:
            urls.append(waybill_render(i[0]))
        return render(request=req, template_name='Avtoregion/waybill.html',
                      context={'qset': qset, 'urls': urls})


def date_to_str(date):
    return date.split(' - ')


def ajax_handler(req):
    if req.is_ajax():
        id_car = req.GET.get('id')
        if id_car is not None:
            try:
                rce = Race.objects.filter(car_id=int(id_car)).latest(field_name='id_race')
                data = json.dumps({'gas_start': float(rce.gas_end), 's_milage': float(rce.e_milage)})
            except ObjectDoesNotExist:
                data = json.dumps({'gas_start': 0, 's_milage': 0})
            finally:
                return HttpResponse(data, content_type='application/json')

        else:
            raise Http404


class AjaxUpdateState(View):
    model = Race

    def post(self, *args, **kwargs):
        if self.request.is_ajax():
            json_data = json.loads(self.request.body.decode('utf-8'))
            try:
                data = json_data['data'][0]
                if len(data['id_list']) != 0:
                    try:
                        for id in data['id_list']:
                            self.model.objects.filter(id_race=int(id)).update(state=data['state'])
                        messages.add_message(self.request, messages.SUCCESS, 'Состояние обновленo.')
                        data = json.dumps({'success': True})
                        return HttpResponse(content=data, content_type='application/json')
                    except ObjectDoesNotExist:
                        messages.add_message(self.request, messages.WARNING, 'Не найдены объекты рейсов в базе данных')
                        data = json.dumps({'success': False})
                        return HttpResponse(content=data, content_type='application/json')
                else:
                    messages.add_message(self.request, messages.WARNING, 'Не выбраны рейсы для обновления статуса.')
                    data = json.dumps({'success': False})
                    return HttpResponse(content=data, content_type='application/json')
            except KeyError:
                messages.add_message(self.request, messages.ERROR, 'Проблемы сервера, обратитесь к администратору')
                HttpResponseServerError('Malformed data!')

