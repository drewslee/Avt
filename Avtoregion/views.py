# -*- coding:utf-8 -*-
import os
import ast
import xlsxwriter
import json
import shutil
import tempfile
import uuid
from zipfile import ZipFile
from operator import __or__ as OR
from functools import reduce
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
from django.contrib.staticfiles import finders
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormMixin, View
from django.views.generic.list import ListView
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.messages import constants as messages_constants
from braces.views import JSONRequestResponseMixin
from Avtoregion.templatetags import custom_filters

from .forms import CarForm
from .forms import CustomAuthForm
from .forms import CustomerForm
from .forms import DriverForm
from .forms import MediatorForm
from .forms import ProductForm
from .forms import RaceForm
from .forms import RaceUpdateForm
from .forms import ShipmentForm
from .forms import SupplierForm
from .forms import TrailerForm
from .forms import ConstantForm
from .forms import UnitsForm
from .forms import LoadForm
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
from .models import LoadingPlace


class LoginViewMix(LoginView):
    form_class = CustomAuthForm


class DeleteViewMixin:
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.has_deleted = True
        self.object.save()
        return HttpResponseRedirect(success_url)

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.request.POST.get('pk'))


class AliveListViewMixin:
    def get_queryset(self):
        return super().get_queryset().exclude(has_deleted=True)


# def get_context_data(self, object_list=None, **kwargs):
#    kwargs = super().get_context_data(**kwargs)
#    kwargs['form'] = exec(str(self.model.__name__) + 'Form()')
#    return kwargs


class ConstantsViewList(PermissionRequiredMixin, FormMixin, ListView):
    model = Constants
    template_name = 'Avtoregion/update_form.html'
    permission_required = ('Avtoregion.change_constants',)
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
            end_date = Race.objects.latest('race_date').race_date
            start_date = end_date - timedelta(weeks=1)
            queryset = Race.objects.filter(race_date__range=[start_date, end_date]).select_related('unit_load',
                                                                                                   'unit_unload',
                                                                                                   'driver', 'car',
                                                                                                   'customer',
                                                                                                   'supplier',
                                                                                                   'product',
                                                                                                   'shipment')
        else:
            start_date, end_date = datestr_to_dateaware(self.request.GET.get('daterange'))
            queryset = Race.objects.filter(race_date__range=[start_date, end_date]).select_related('unit_load',
                                                                                                   'unit_unload',
                                                                                                   'driver', 'car',
                                                                                                   'customer',
                                                                                                   'supplier',
                                                                                                   'product',
                                                                                                   'shipment')
        return queryset

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['select_state'] = (x[1] for x in self.model.STATE)
        if self.request.GET.get('daterange') is not None:
            start_date, end_date = datestr_to_dateaware(self.request.GET.get('daterange'))
            ctx['start_date'] = str(start_date)
            ctx['end_date'] = str(end_date)
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
    permission_required = ('Avtoregion.add_race',)


class RaceUpdate(SuccessMessageMixin, PermissionRequiredMixin, UpdateView):
    model = Race
    form_class = RaceUpdateForm
    template_name = 'Avtoregion/race_update_form.html'
    success_message = "Рейс обновлён успешно"
    permission_required = ('Avtoregion.change_race',)

    def get_success_url(self):
        if self.request.POST.get('previous'):
            return self.request.POST.get('previous')
        else:
            return super(UpdateView, self).get_success_url()


class RaceDelete(PermissionRequiredMixin, JSONRequestResponseMixin, View):
    model = Race
    permission_required = ('Avtoregion.delete_race',)

    def post(self, request, *args, **kwargs):
        ids = self.request_json.get('id_list')
        if ids:
            for id in ids:
                queryset = self.model.objects.filter(pk=id)
                queryset.get().delete()
        return self.render_json_response({'data': 'success'})

    def handle_no_permission(self):
        return self.render_json_response({'data': 'denied'})


class CarViewList(LoginRequiredMixin, AliveListViewMixin, ListView):
    model = Car
    template_name = 'car.html'
    context_object_name = 'qCar'

    def get_context_data(self, object_list=None, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['form'] = CarForm()
        return kwargs


class TrailerViewList(LoginRequiredMixin, AliveListViewMixin, ListView):
    model = Trailer
    template_name = 'trailer.html'
    context_object_name = 'qTrailer'

    def get_context_data(self, object_list=None, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['form'] = TrailerForm()
        return kwargs


class UnitsViewList(LoginRequiredMixin, AliveListViewMixin, ListView):
    model = Units
    template_name = 'units.html'
    context_object_name = 'qUnits'

    def get_context_data(self, object_list=None, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['form'] = UnitsForm()
        return kwargs


class DriverViewList(LoginRequiredMixin, AliveListViewMixin, ListView):
    model = Driver
    template_name = 'driver.html'
    context_object_name = 'qDriver'

    def get_context_data(self, object_list=None, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['form'] = DriverForm()
        return kwargs


class ProductViewList(LoginRequiredMixin, AliveListViewMixin, ListView):
    model = Product
    template_name = 'product.html'
    context_object_name = 'qProduct'

    def get_context_data(self, object_list=None, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['form'] = ProductForm()
        return kwargs


class CustomerViewList(LoginRequiredMixin, AliveListViewMixin, ListView):
    model = Customer
    template_name = 'customer.html'
    context_object_name = 'qCustomer'

    def get_context_data(self, object_list=None, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['form'] = CustomerForm()
        return kwargs


class SupplierViewList(LoginRequiredMixin, AliveListViewMixin, ListView):
    model = Supplier
    template_name = 'supplier.html'
    context_object_name = 'qSupplier'

    def get_context_data(self, object_list=None, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['form'] = SupplierForm()
        return kwargs


class ShipmentViewList(LoginRequiredMixin, AliveListViewMixin, View):
    model = Shipment
    template_name = 'shipment.html'

    def get(self, *args, **kwargs):
        context = {}
        customer = int(self.kwargs.get('customer'))
        context['qShipment'] = self.model.objects.filter(customer=customer, has_deleted=False)
        context['form'] = ShipmentForm(initial={'customer': customer})
        context['customer'] = customer
        return render(self.request, self.template_name, context)


class LoadPlaceViewList(LoginRequiredMixin, AliveListViewMixin, View):
    model = LoadingPlace
    template_name = 'loadplace.html'

    def get(self, *args, **kwargs):
        context = {}
        supplier = int(self.kwargs.get('supplier'))
        context['qLoadplace'] = self.model.objects.filter(supplier=supplier, has_deleted=False)
        context['form'] = LoadForm(initial={'supplier': supplier})
        context['supplier'] = supplier
        return render(self.request, self.template_name, context)


class MediatorViewList(LoginRequiredMixin, AliveListViewMixin, ListView):
    model = Mediator
    template_name = 'mediator.html'
    context_object_name = 'qMediator'

    def get_context_data(self, object_list=None, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['form'] = MediatorForm()
        return kwargs


class LoadAdd(PermissionRequiredMixin, CreateView):
    model = LoadingPlace
    form_class = LoadForm
    permission_required = ('Avtoregion.add_loadingplace',)

    def get_success_url(self):
        if self.request.POST.get('previous'):
            return self.request.POST.get('previous')
        else:
            return super(CreateView, self).get_success_url()


class LoadUpdate(PermissionRequiredMixin, UpdateView):
    model = LoadingPlace
    form_class = LoadForm
    permission_required = ('Avtoregion.change_loadingplace',)

    def get_success_url(self):
        if self.request.POST.get('previous'):
            return self.request.POST.get('previous')
        else:
            return super(UpdateView, self).get_success_url()


class LoadDelete(PermissionRequiredMixin, DeleteViewMixin, DeleteView):
    model = LoadingPlace
    permission_required = ('Avtoregion.delete_loadingplace',)

    def get_success_url(self):
        return reverse_lazy('LoadPlaceList', kwargs={'supplier': self.kwargs['supplier']})


class DriverAdd(PermissionRequiredMixin, CreateView):
    model = Driver
    success_url = reverse_lazy('DriverList')
    form_class = DriverForm
    permission_required = ('Avtoregion.add_driver',)


class DriverUpdate(PermissionRequiredMixin, UpdateView):
    model = Driver
    success_url = reverse_lazy('DriverList')
    form_class = DriverForm
    permission_required = ('Avtoregion.change_driver',)


class DriverDelete(PermissionRequiredMixin, DeleteViewMixin, DeleteView):
    model = Driver
    success_url = reverse_lazy('DriverList')
    permission_required = ('Avtoregion.delete_driver',)


class SupplierAdd(PermissionRequiredMixin, CreateView):
    model = Supplier
    success_url = reverse_lazy('SupplierList')
    form_class = SupplierForm
    permission_required = ('Avtoregion.add_supplier',)


class SupplierUpdate(PermissionRequiredMixin, UpdateView):
    model = Supplier
    success_url = reverse_lazy('SupplierList')
    form_class = SupplierForm
    permission_required = ('Avtoregion.change_supplier',)


class SupplierDelete(PermissionRequiredMixin, DeleteViewMixin, DeleteView):
    model = Supplier
    success_url = reverse_lazy('SupplierList')
    permission_required = ('Avtoregion.delete_supplier',)


class UnitAdd(PermissionRequiredMixin, CreateView):
    model = Units
    success_url = reverse_lazy('UnitList')
    form_class = UnitsForm
    permission_required = ('Avtoregion.add_unit',)


class UnitUpdate(PermissionRequiredMixin, UpdateView):
    model = Units
    success_url = reverse_lazy('UnitList')
    form_class = UnitsForm
    permission_required = ('Avtoregion.change_unit',)


class UnitDelete(PermissionRequiredMixin, DeleteViewMixin, DeleteView):
    model = Units
    success_url = reverse_lazy('UnitList')
    permission_required = ('Avtoregion.delete_unit',)


class CarAdd(PermissionRequiredMixin, CreateView):
    model = Car
    success_url = reverse_lazy('CarList')
    form_class = CarForm
    permission_required = ('Avtoregion.add_car',)


class CarUpdate(PermissionRequiredMixin, UpdateView):
    model = Car
    success_url = reverse_lazy('CarList')
    form_class = CarForm
    permission_required = ('Avtoregion.change_car',)


class CarDelete(PermissionRequiredMixin, DeleteViewMixin, DeleteView):
    model = Car
    success_url = reverse_lazy('CarList')
    permission_required = ('Avtoregion.delete_car',)


class ProductAdd(PermissionRequiredMixin, CreateView):
    model = Product
    success_url = reverse_lazy('ProductList')
    form_class = ProductForm
    permission_required = ('Avtoregion.add_product',)


class ProductUpdate(PermissionRequiredMixin, UpdateView):
    model = Product
    success_url = reverse_lazy('ProductList')
    form_class = ProductForm
    permission_required = ('Avtoregion.change_product',)


class ProductDelete(PermissionRequiredMixin, DeleteViewMixin, DeleteView):
    model = Product
    success_url = reverse_lazy('ProductList')
    permission_required = ('Avtoregion.delete_product',)


class TrailerAdd(PermissionRequiredMixin, CreateView):
    model = Trailer
    success_url = reverse_lazy('TrailerList')
    form_class = TrailerForm
    permission_required = ('Avtoregion.add_trailer',)


class TrailerUpdate(PermissionRequiredMixin, UpdateView):
    model = Trailer
    success_url = reverse_lazy('TrailerList')
    form_class = TrailerForm
    permission_required = ('Avtoregion.change_trailer',)


class TrailerDelete(PermissionRequiredMixin, DeleteViewMixin, DeleteView):
    model = Trailer
    success_url = reverse_lazy('TrailerList')
    permission_required = ('Avtoregion.delete_trailer',)


class ShipmentAdd(PermissionRequiredMixin, CreateView):
    model = Shipment
    form_class = ShipmentForm
    permission_required = ('Avtoregion.add_shipment',)

    def get_success_url(self):
        if self.request.POST.get('previous'):
            return self.request.POST.get('previous')
        else:
            return super(CreateView, self).get_success_url()


class ShipmentUpdate(PermissionRequiredMixin, UpdateView):
    model = Shipment
    form_class = ShipmentForm
    permission_required = ('Avtoregion.change_shipment',)

    def get_success_url(self):
        if self.request.POST.get('previous'):
            return self.request.POST.get('previous')
        else:
            return super(UpdateView, self).get_success_url()


class ShipmentDelete(PermissionRequiredMixin, DeleteViewMixin, DeleteView):
    model = Shipment
    permission_required = ('Avtoregion.delete_shipment',)

    def get_success_url(self):
        return reverse_lazy('ShipmentList', kwargs={'customer': self.kwargs['customer']})


class MediatorAdd(PermissionRequiredMixin, CreateView):
    model = Mediator
    success_url = reverse_lazy('MediatorList')
    form_class = MediatorForm
    permission_required = ('Avtoregion.add_mediator',)


class MediatorUpdate(PermissionRequiredMixin, UpdateView):
    model = Mediator
    success_url = reverse_lazy('MediatorList')
    form_class = MediatorForm
    permission_required = ('Avtoregion.change_mediator',)


class MediatorDelete(PermissionRequiredMixin, DeleteViewMixin, DeleteView):
    model = Mediator
    success_url = reverse_lazy('MediatorList')
    permission_required = ('Avtoregion.delete_mediator',)


class CustomerAdd(PermissionRequiredMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    success_url = reverse_lazy('CustomerList')
    permission_required = ('Avtoregion.add_customer',)


class CustomerUpdate(PermissionRequiredMixin, UpdateView):
    model = Customer
    success_url = reverse_lazy('CustomerList')
    form_class = CustomerForm
    permission_required = ('Avtoregion.change_customer',)


class CustomerDelete(PermissionRequiredMixin, DeleteViewMixin, DeleteView):
    model = Customer
    success_url = reverse_lazy('CustomerList')
    permission_required = ('Avtoregion.delete_customer',)


class Accumulate(JSONRequestResponseMixin, View):
    def dispatch_method(self, value):
        method_name = 'get_query_' + str(value)
        return getattr(self, method_name)

    def get(self, *args, **kwargs):
        q_sup = Supplier.objects.all()
        q_prod = Product.objects.all()
        q_cus = Customer.objects.all()
        q_med = Mediator.objects.all()
        context = {'q_sup': q_sup, 'q_cus': q_cus, 'q_med': q_med, 'q_prod': q_prod,
                   'race_type': (Race.TYPE[0][0], Race.TYPE[1][0]),
                   'state': (Race.CREATE, Race.LOAD, Race.UNLOAD, Race.FINISH, Race.END, Race.ACCIDENT)}
        return render(request=self.request, template_name='Avtoregion/account.html', context=context)

    def post(self, *args, **kwargs):
        start_date, end_date = datestr_to_dateaware(self.request_json.get('daterange'))

        q_resp, q_weight, type_prod = {}, {}, ""

        ctx = {
            'supplier': self.request_json.get('supplier'),
            'customer': self.request_json.get('customer'),
            'mediator': self.request_json.get('mediator'),
        }

        for key, value in ctx.items():
            if value is not None:
                method = self.dispatch_method(key)
                q_resp, q_weight, type_prod = method([start_date, end_date])

        select_state = (x[1] for x in Race.STATE)
        table = render_to_string(template_name='table.html',
                                 context={'q_resp': q_resp, 'q_weight': q_weight, 'type_name': type_prod,
                                          'start_date': start_date, 'end_date': end_date - timedelta(days=1),
                                          'select_state': select_state})
        return self.render_json_response({"data": table})

    def get_query_supplier(self, date):
        type_prod = 'supplier'
        query = Q(type_ship__exact=self.request_json.get('service'),
                  supplier_id=self.request_json.get('supplier'),
                  race_date__range=date)
        query = self.get_query_product(query)
        query = self.get_query_state(query)

        q_resp = Race.objects.filter(query).order_by('race_date').filter(weight_load__gt=0)
        q_weight = q_resp.aggregate(Sum('weight_load'))
        q_resp.select_related('car', 'driver', 'product')
        return q_resp, q_weight, type_prod

    def get_query_customer(self, date):
        type_prod = 'customer'
        query = Q(customer_id=self.request_json['customer'],
                  race_date__range=date)

        query = self.get_query_product(query)
        query = self.get_query_state(query)

        if self.request_json.get('unload_place').strip():
            query.add(Q(shipment_id=self.request_json['unload_place']), Q.AND)

        q_resp = Race.objects.filter(query).order_by('race_date').filter(weight_unload__gt=0)
        q_weight = q_resp.aggregate(Sum('weight_unload'))
        q_resp.select_related('car', 'driver', 'product')
        return q_resp, q_weight, type_prod

    def get_query_mediator(self, date):
        type_prod = 'mediator'
        query = Q(car__mediator__id_mediator=self.request_json['mediator'],
                  race_date__range=date)

        query = self.get_query_product(query)
        query = self.get_query_state(query)

        q_resp = Race.objects.filter(query).order_by('race_date').filter(weight_load__gt=0)
        q_weight = q_resp.aggregate(Sum('weight_load'))
        return q_resp, q_weight, type_prod

    def get_query_product(self, query):
        if self.request_json['product']:
            prod = self.request_json['product']
            if len(prod) == 1:
                query.add(Q(product__name=prod[0]), Q.AND)
            else:
                lst = []
                for v in prod:
                    lst.append(Q(product__name=v))
                query.add(reduce(OR, lst), Q.AND)
        return query

    def get_query_state(self, query):
        if self.request_json.get('state'):
            query.add(Q(state=self.request_json.get('state')), Q.AND)
        return query


class CarResponce(View):
    def get(self, *args, **kwargs):
        qset = Car.objects.all()
        return render(request=self.request, template_name='Avtoregion/accumulate_car.html', context={'qset': qset})

    def post(self, *args, **kwargs):
        start_date, end_date = datestr_to_dateaware(self.request.POST['daterange'])
        q_resp = Race.objects.filter(car__number__exact=self.request.POST.get('car'),
                                     race_date__range=[start_date, end_date]).order_by('race_date')
        return render(request=self.request, template_name='Avtoregion/account_car.html',
                      context={'q_resp': q_resp})


class DriverResponce(View):
    def get(self, *args, **kwargs):
        qset = Driver.objects.all()
        return render(request=self.request, template_name='Avtoregion/accumulate_driver.html', context={'qset': qset})

    def post(self, *args, **kwargs):
        start_date, end_date = datestr_to_dateaware(self.request.POST['daterange'])
        q_resp = Race.objects.filter(driver__name__exact=self.request.POST.get('driver'),
                                     race_date__range=[start_date, end_date]).order_by('race_date')
        return render(request=self.request, template_name='Avtoregion/account_driver.html',
                      context={'q_resp': q_resp})


def save_excel(request):
    filename = 'name'
    json_data = json.loads(request.body.decode('utf-8'))
    json_data = ast.literal_eval(json_data)
    org = json_data.pop('org')
    start_date = json_data.pop('start_date')
    end_date = json_data.pop('end_date')
    response = HttpResponse(content_type='vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename={}.xlsx'.format(filename)

    wb = xlsxwriter.Workbook(response, {'in_memory': True})
    ws = wb.add_worksheet(name='List1')
    format = wb.add_format({
        'bold': True,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
    })
    format_border = wb.add_format({'border': 1})
    ws.set_column('A:A', 1)
    ws.set_column('B:B', 5)
    ws.set_column('C:C', 10)
    ws.set_column('D:D', 18)
    ws.set_column('E:E', 20)
    ws.set_column('F:F', 10)
    ws.set_column('G:G', 18)
    ws.set_column('H:H', 5)

    # Sheet header, first row
    ws.merge_range('A1:G2',
                   'РЕЕСТР ПЕРЕВОЗОК {} - {} \n за период с {} по {}'.format('ООО \"Авторегион\"',
                                                                             org,
                                                                             start_date,
                                                                             end_date),
                   format)
    col = 0
    for title in ['', '№', 'Дата', 'Номер машины', 'Водитель', 'Вес', 'Груз', 'Ед.', 'Плечо', 'Кол-во рейсов', 'Состояние']:
        ws.write_string(3, col, title, format)
        col += 1
    i = 0
    row = 4
    while i < len(json_data):
        col = 0
        for value in json_data.get(str(i)):
            if col == 5:
                ws.write_number(row, col, float(value.replace(',', '.')), format_border)
            else:
                ws.write(row, col, value, format_border)
            col += 1
        row += 1
        i += 1
    else:
        ws.merge_range('A{}:D{}'.format(row + 1, row + 1), 'ИТОГО:', format)
        ws.write_formula(row, 4, '=SUM(E5:E{})'.format(row), format)
        ws.write_string(row + 2, 0, 'Исполнительный директор ООО "Авторегион"     ___________/Денисов А.Н./')

    return response


def ooxml_render(race_id, prefname, template_name, tmp_name):
    static_root = djangoSettings.STATIC_ROOT
    const = Constants.objects.get(id=1)
    race = Race.objects.get(id_race=int(race_id))
    buf = render_to_string(template_name, {'race': race, 'const': const})
    filename = prefname + '_' + str(race_id) + '_' + (timezone.datetime.now().strftime('%y_%m_%d_%H_%M_%S'))
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpf_name = os.path.join(tmpdir, tmp_name)
        shutil.copytree(os.path.join(static_root, tmp_name), tmpf_name)
        with open(os.path.join(tmpf_name, 'xl', 'sharedStrings.xml', ), 'w', newline='\r\n') as f:
            f.write(buf)
        shutil.make_archive(os.path.join(static_root, 'temp', filename), 'zip', tmpf_name, '.')
    os.rename(os.path.join(static_root, 'temp', filename + '.zip'),
              os.path.join(static_root, 'temp', filename + '.xlsx'))
    return '/'.join(['temp', filename + '.xlsx']), filename + '.xlsx'


def datestr_to_dateaware(date):
    start_date, end_date = date.split(' - ')
    start_date = timezone.make_aware(timezone.datetime.strptime(start_date, '%Y-%m-%d'), timezone=timezone.utc)
    end_date = timezone.make_aware(timezone.datetime.strptime(end_date, '%Y-%m-%d'),
                                   timezone=timezone.utc) + timedelta(days=1)
    return start_date, end_date


def ajax_track(req):
    if req.is_ajax():
        data = json.dumps({'gas_start': 0, 's_milage': 0})
        if req.GET.get('id').strip():
            rce = Race.objects.filter(car_id=int(req.GET.get('id'))).latest(field_name='id_race')
            data = json.dumps({'gas_start': float(rce.gas_end), 's_milage': float(rce.e_milage)})
        return HttpResponse(data, content_type='application/json')


def ajax_sup(req):
    if req.is_ajax():
        data = {}
        if req.GET.get('id').strip():
            sup = list(LoadingPlace.objects.filter(supplier=int(req.GET.get('id'))).values())
            data = json.dumps(sup)
        return HttpResponse(data, content_type='application/json')


def get_unload_place(req):
    if req.is_ajax():
        data = {}
        if req.GET.get('id').strip():
            cus = list(Shipment.objects.filter(customer=int(req.GET.get('id'))).values())
            data = json.dumps(cus)
        return HttpResponse(data, content_type='application/json')


class AjaxUpdateState(JSONRequestResponseMixin, View):
    require_json = True
    model = Race

    def post(self, request, *args, **kwargs):
        ids = self.request_json.get('id_list')
        print(ids)
        state = self.request_json.get('state')
        print(state)
        if ids:
            for id in ids:
                self.model.objects.filter(id_race=int(id)).update(state=state)
            messages.add_message(self.request, messages.SUCCESS, 'Состояние обновленo.')
        return self.render_json_response({'data': 'success'})


class PackingView(JSONRequestResponseMixin, View):
    require_json = True

    def post(self, request, *args, **kwargs):
        files = {'urls': [], 'filenames': [], 'paths': []}
        ids = self.request_json.get("id_list")
        if ids:
            for i in ids:
                url, filename = ooxml_render(i, 'packing', 'sharedStrings2.xml', 'packing')
                files['urls'].append(url)
                files['filenames'].append(filename)
                files['paths'].append(finders.find(url))
        uuidname = str(uuid.uuid4()) + '.zip'
        urlzipfile = '/'.join(['temp', uuidname])
        zipfilename = os.path.join(djangoSettings.STATIC_ROOT, 'temp', uuidname)

        with ZipFile(zipfilename, 'w') as myzip:
            for path in files['paths']:
                myzip.write(path, os.path.basename(path))
        templated = render_to_string(template_name='Avtoregion/result_list.html', context={'urls': files['urls'],
                                                                                           'filenames': files[
                                                                                               'filenames'],
                                                                                           'zipfilename': urlzipfile,
                                                                                           'name': 'Товарная накладная'})
        return self.render_json_response({'data': templated})


class WayView(JSONRequestResponseMixin, View):
    require_json = True

    def post(self, request, *args, **kwargs):
        files = {'urls': [], 'filenames': [], 'paths': []}
        ids = self.request_json.get("id_list")
        if ids:
            for i in ids:
                url, filename = ooxml_render(i, 'way', 'sharedStrings.xml', 'way')
                files['urls'].append(url)
                files['filenames'].append(filename)
                files['paths'].append(finders.find(url))
        uuidname = str(uuid.uuid4()) + '.zip'
        urlzipfile = '/'.join(['temp', uuidname])
        zipfilename = os.path.join(djangoSettings.STATIC_ROOT, 'temp', uuidname)
        with ZipFile(zipfilename, 'w') as myzip:
            for path in files['paths']:
                myzip.write(path, os.path.basename(path))
        templated = render_to_string(template_name='Avtoregion/result_list.html', context={'urls': files['urls'],
                                                                                           'filenames': files[
                                                                                               'filenames'],
                                                                                           'zipfilename': urlzipfile,
                                                                                           "name": 'Путевой лист'})
        return self.render_json_response({'data': templated})
