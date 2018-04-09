# -*- coding:utf-8 -*-
import os
import ast
import xlsxwriter
import json
import shutil
import tempfile
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
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormMixin, View
from django.views.generic.list import ListView
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.messages import constants as messages_constants
from django.views.decorators.cache import never_cache
from braces.views import CsrfExemptMixin, JSONRequestResponseMixin
from Avtoregion.templatetags import hyphen_string

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
            end_date = Race.objects.latest().race_date
            start_date = end_date - timedelta(weeks=1)
            queryset = Race.objects.filter(race_date__range=[start_date, end_date]).order_by(
                'race_date')
        else:
            start_date, end_date = datestr_to_dateaware(self.request.GET.get('daterange'))
            queryset = Race.objects.filter(race_date__range=[start_date, end_date]).order_by('race_date')
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
    success_message = "Рейс создан успешно"
    permission_required = ('Avtoregion.add_race',)


class RaceUpdate(SuccessMessageMixin, PermissionRequiredMixin, UpdateView):
    model = Race
    form_class = RaceForm
    template_name = 'Avtoregion/race_update_form.html'
    success_message = "Рейс обновлён успешно"
    permission_required = ('Avtoregion.change_race',)

    def get_success_url(self):
        if self.request.POST.get('priveous'):
            return self.request.POST.get('priveous')
        else:
            return super(UpdateView, self).get_success_url()


class RaceDelete(SuccessMessageMixin, PermissionRequiredMixin, DeleteView):
    model = Race
    success_url = '/Race'
    success_message = "Рейс удалён"
    permission_required = ('Avtoregion.delete_race',)

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


class ShipmentViewList(LoginRequiredMixin, View):
    model = Shipment
    template_name = 'shipment.html'

    def post(self, *args, **kwargs):
        context = {}
        customer = int(self.request.POST.get('customer'))
        context['qShipment'] = self.model.objects.filter(customer=customer)
        context['form'] = ShipmentForm(initial={'customer': customer})
        context['customer'] = customer
        return render(self.request, self.template_name, context)


class LoadPlaceViewList(LoginRequiredMixin, View):
    model = LoadingPlace
    template_name = 'loadplace.html'

    def post(self, *args, **kwargs):
        context = {}
        supplier = int(self.request.POST.get('supplier'))
        context['qLoadplace'] = self.model.objects.filter(supplier=supplier)
        context['form'] = LoadForm(initial={'supplier': supplier})
        context['supplier'] = supplier
        return render(self.request, self.template_name, context)


class MediatorViewList(LoginRequiredMixin, ListView):
    model = Mediator
    template_name = 'mediator.html'
    context_object_name = 'qMediator'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = MediatorForm()
        return context


class LoadAdd(PermissionRequiredMixin, CreateView):
    model = LoadingPlace
    success_url = reverse_lazy('SupplierList')
    form_class = LoadForm
    permission_required = ('Avtoregion.add_loadingplace',)


class LoadUpdate(PermissionRequiredMixin, UpdateView):
    model = LoadingPlace
    success_url = reverse_lazy('SupplierList')
    form_class = LoadForm
    permission_required = ('Avtoregion.change_loadingplace',)


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


class DriverDelete(PermissionRequiredMixin, DeleteView):
    model = Driver
    success_url = reverse_lazy('DriverList')
    permission_required = ('Avtoregion.delete_driver',)

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.request.POST.get('pk'))


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


class SupplierDelete(PermissionRequiredMixin, DeleteView):
    model = Supplier
    success_url = reverse_lazy('SupplierList')
    permission_required = ('Avtoregion.delete_supplier',)

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.request.POST.get('pk'))


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


class UnitDelete(PermissionRequiredMixin, DeleteView):
    model = Units
    success_url = reverse_lazy('UnitList')
    permission_required = ('Avtoregion.delete_unit',)

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.request.POST.get('pk'))


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


class CarDelete(PermissionRequiredMixin, DeleteView):
    model = Car
    success_url = reverse_lazy('CarList')
    permission_required = ('Avtoregion.delete_car',)

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.request.POST.get('pk'))


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


class ProductDelete(PermissionRequiredMixin, DeleteView):
    model = Product
    success_url = reverse_lazy('ProductList')
    permission_required = ('Avtoregion.delete_product',)

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.request.POST.get('pk'))


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


class TrailerDelete(PermissionRequiredMixin, DeleteView):
    model = Trailer
    success_url = reverse_lazy('TrailerList')
    permission_required = ('Avtoregion.delete_trailer',)

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.request.POST.get('pk'))


class ShipmentAdd(PermissionRequiredMixin, CreateView):
    model = Shipment
    success_url = reverse_lazy('CustomerList')
    form_class = ShipmentForm
    permission_required = ('Avtoregion.add_shipment',)


class ShipmentUpdate(PermissionRequiredMixin, UpdateView):
    model = Shipment
    success_url = reverse_lazy('CustomerList')
    form_class = ShipmentForm
    permission_required = ('Avtoregion.change_shipment',)


class ShipmentDelete(PermissionRequiredMixin, DeleteView):
    model = Shipment
    success_url = reverse_lazy('CustomerList')
    permission_required = ('Avtoregion.delete_shipment',)

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.request.POST.get('pk'))


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


class MediatorDelete(PermissionRequiredMixin, DeleteView):
    model = Mediator
    success_url = reverse_lazy('MediatorList')
    permission_required = ('Avtoregion.delete_mediator',)

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.request.POST.get('pk'))


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


class CustomerDelete(PermissionRequiredMixin, DeleteView):
    model = Customer
    success_url = reverse_lazy('CustomerList')
    permission_required = ('Avtoregion.delete_customer',)

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.request.POST.get('pk'))


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

        table = render_to_string(template_name='table.html',
                                 context={'q_resp': q_resp, 'q_weight': q_weight, 'type_name': type_prod,
                                          'start_date': start_date, 'end_date': end_date - timedelta(days=1)})
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
    ws.set_column('A:A', 5)
    ws.set_column('B:B', 20)
    ws.set_column('C:C', 20)
    ws.set_column('D:D', 20)
    ws.set_column('F:F', 20)
    ws.set_column('G:G', 5)

    # Sheet header, first row
    ws.merge_range('A1:G2',
                   'РЕЕСТР ПЕРЕВОЗОК {} - {} \n за период с {} по {}'.format('ООО \"Авторегион\"',
                                                                                                 org,
                                                                                                 start_date,
                                                                                                 end_date),
                   format)
    col = 0
    for title in ['№', 'Дата', 'Номер машины', 'Водитель', 'Вес', 'Груз', 'Ед.']:
        ws.write_string(3, col, title, format)
        col += 1
    i = 0
    row = 4
    while i < len(json_data):
        col = 0
        for value in json_data.get(str(i)):
            if col == 4:
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
    return '/'.join(['temp', filename + '.xlsx'])


class Waybill(View):
    queryset = Car.objects.all()

    def get(self, request, *args, **kwargs):
        return render(request=request, template_name='Avtoregion/waybill.html', context={'qset': self.queryset})

    def post(self, request, *args, **kwargs):
        start_date, end_date = datestr_to_dateaware(request.POST['daterange'])
        q_resp = Race.objects.filter(car__number__exact=request.POST.get('car'),
                                     race_date__range=[start_date, end_date])
        urls = []
        idlist = q_resp.values_list('id_race')
        for i in idlist:
            urls.append(ooxml_render(i[0], 'waybill', 'sharedStrings.xml', 'way'))
        return render(request=request, template_name='Avtoregion/waybill.html',
                      context={'qset': self.queryset, 'urls': urls})


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
                    except self.model.DoesNotExist:
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


class PackingView(JSONRequestResponseMixin, View):
    require_json = True

    def post(self, request, *args, **kwargs):
        urls = []
        ids = self.request_json["id_list"]
        if ids:
            for id in ids:
                urls.append(ooxml_render(id, 'packing', 'sharedStrings2.xml', 'packing'))
        templated = render_to_string(template_name='Avtoregion/result_list.html', context={'urls': urls})
        return self.render_json_response({'data': templated})
