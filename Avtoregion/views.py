# -*- coding:utf-8 -*-
import os
import xlwt
import openpyxl
import json
from openpyxl.styles.borders import Border, Side
from openpyxl.styles import NamedStyle
from django.http.response import HttpResponseRedirect,Http404, HttpResponse
from django.conf import settings as djangoSettings
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormMixin
from django.views.generic.list import ListView
from django.core.exceptions import ObjectDoesNotExist

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
from .models import Car
from .models import Customer
from .models import Driver
from .models import Mediator
from .models import Product
from .models import Race
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


class RaceAllList(LoginRequiredMixin, ListView):
    model = Race
    template_name = 'race.html'
    context_object_name = 'qRace'
    paginate_by = 7
    queryset = Race.objects.order_by('id_race')


class RaceViewList(LoginRequiredMixin, ListView):
    model = Race
    template_name = 'race_date.html'
    context_object_name = 'qRace'
    paginate_by = 7

    def get_queryset(self):
        if self.request.GET.get('daterange') is None:
            queryset = Race.objects.filter(race_date__range=[timezone.now().date(), timezone.now().date()]).order_by('id_race')
        else:
            start_date, end_date = date_to_str(self.request.GET.get('daterange'))
            queryset = Race.objects.filter(race_date__range=[start_date, end_date]).order_by('id_race')
        return queryset

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.GET.get('daterange') is not None:
            start_date, end_date = date_to_str(self.request.GET.get('daterange'))
        else:
            start_date = timezone.now().date()
            end_date = timezone.now().date()
        ctx['start_date'] = str(start_date)
        ctx['end_date'] = str(end_date)
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
        fields = [field.name for field in Race._meta.fields]
        fields.remove('weight_unload')
        fields_list = ['race_date', 'car__number', 'weight_load', 'product__name']
        query = Q(supplier__id_supplier__exact=req.POST.get('supplier'),
                  race_date__range=[start_date, end_date]
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
        filename = save_excel('supplier', q_resp.values_list(*fields_list), ['Дата', 'Номер', 'Вес', 'Фракция'])

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
        start_date, end_date = date_to_str(req.POST['daterange'])
        fields = [field.name for field in Race._meta.fields]
        fields_list = ['race_date', 'car__number', 'weight_unload', 'product__name']
        fields.remove('weight_load')
        query = Q(customer__id_customer__exact=req.POST.get('customer'),
                  race_date__range=[start_date, end_date]
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
        filename = save_excel('customer', q_resp.values_list(*fields_list), ['Дата', 'Номер', 'Вес', 'Фракция'])
        return render(request=req, template_name='Avtoregion/account.html',
                      context={'q_resp': q_resp, 'q_weight': q_weight, 'filename': filename})


def accumulate_car(req):
    qset = Car.objects.all()
    if req.method == 'GET':
        return render(request=req, template_name='Avtoregion/accumulate_car.html', context={'qset': qset})
    if req.method == 'POST':
        start_date, end_date = date_to_str(req.POST['daterange'])
        q_resp = Race.objects.filter(car__number__exact=req.POST.get('car'),
                                     race_date__range=[start_date, end_date])
        field_list = ['race_date', 'id_race', 'car__number', 'driver__name', 'type_ship', 'supplier__name',
                      'customer__name', 'shipment__name', 'product__name', 's_milage', 'e_milage', 'weight_load',
                      'weight_unload', 'state']
        col = (
            'Дата', 'Номер рейса', 'Номер машины', 'Водитель', 'Реализация', 'Поставщик', 'Клиент', 'Место разгрузки',
            'Товар',
            'Начало трека', 'Конец трека', 'Загружено', 'Выгружено', 'Состояние')
        filename = save_excel('car', q_resp.values_list(*field_list), col)
        return render(request=req, template_name='Avtoregion/account_car.html',
                      context={'q_resp': q_resp, 'filename': filename})


def accumulate_driver(req):
    qset = Driver.objects.all()
    if req.method == 'GET':
        return render(request=req, template_name='Avtoregion/accumulate_driver.html', context={'qset': qset})
    if req.method == 'POST':
        start_date, end_date = date_to_str(req.POST['daterange'])
        q_resp = Race.objects.filter(driver__name__exact=req.POST.get('driver'),
                                     race_date__range=[start_date, end_date])
        field_list = ['race_date', 'id_race', 'car__number', 'driver__name', 'type_ship', 'supplier__name',
                      'customer__name', 'shipment__name', 'product__name', 's_milage', 'e_milage', 'weight_load',
                      'weight_unload', 'state']
        col = (
            'Дата', 'Номер рейса', 'Номер машины', 'Водитель', 'Реализация', 'Поставщик', 'Клиент', 'Место разгрузки',
            'Товар',
            'Начало трека', 'Конец трека', 'Загружено', 'Выгружено', 'Состояние')
        filename = save_excel('driver', q_resp.values_list(*field_list), col)
        return render(request=req, template_name='Avtoregion/account_driver.html',
                      context={'q_resp': q_resp, 'filename': filename})


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
    filename = 'waybill_'
    thin_border = Border(left=Side(style='thin'),
                         right=Side(style='thin'),
                         top=Side(style='thin'),
                         bottom=Side(style='thin'))
    thick_border = Border(left=Side(style='thick'),
                          right=Side(style='thick'),
                          top=Side(style='thick'),
                          bottom=Side(style='thick'))
    cell_style = NamedStyle(border=thick_border)
    wb = openpyxl.load_workbook(os.path.join(djangoSettings.BASE_DIR, 'static', 'way.xlsx'))
    ws1 = wb['1']
    ws2 = wb['2']
    const = Constants.objects.get(id=1)
    race = Race.objects.get(id_race=int(race_id))
    track = int(race.e_milage) - int(race.s_milage)

    ws1['BG5'] = race.race_date
    ws1['Q6'] = const.organization_unit_full
    ws1['Q13'] = race.car.brand
    ws1['AB14'] = race.car.number
    ws1['CI14'] = race.car.garage_number
    ws1['I21'] = race.car.trailer.brand_trailer
    ws1['CI21'] = race.car.trailer.garage_number_trailer
    ws1['AR21'] = race.car.trailer.number
    ws1['I15'] = race.driver.name
    ws1['P17'] = race.driver.driver_card
    ws1['CI15'] = race.driver.personnel_number
    ws1['DM14'] = race.race_date
    ws1['DM15'] = race.race_date
    ws1['EV14'] = race.s_milage
    ws1['EV15'] = race.e_milage
    ws1['DN24'] = race.gas_given
    ws1['N43'] = race.gas_given
    ws1['DY24'] = race.gas_start
    ws1['EG24'] = race.gas_end
    ws1['V45'] = const.dispatcher
    ws1['CO43'] = const.mechanic
    ws1['CO45'] = race.driver.name
    ws1['CF51'] = race.driver.name
    ws1['CF53'] = const.mechanic
    ws1['DP36'] = race.product.name
    ws1['A36'] = const.organization_unit_small
    ws1['AT36'] = race.supplier.name + race.supplier.address
    ws1['CE36'] = race.customer.name + race.customer.address
    ws1['FL36'] = track
    ws2['DP36'] = track
    ws2['I36'] = int(race.gas_end) - int(race.gas_start)
    ws2['DX36'] = race.shoulder
    ws2['EF36'] = race.shoulder
    ws2['AL7'] = race.race_date
    ws2['AL8'] = race.race_date
    ws2['A7'] = race.supplier.address
    ws2['A8'] = race.customer.address

    filename = filename + str(race_id) + (timezone.datetime.now().strftime('%y_%m_%d_%H_%M_%S')) + '.xlsx'
    path_for_save = os.path.join(djangoSettings.BASE_DIR, 'static', 'temp', filename)
    wb.save(path_for_save)
    wb.close()
    return '/'.join(['temp', filename])


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


def ajaxhandler(req):
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
