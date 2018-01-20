"""Avtoregion URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.urls import reverse_lazy
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(next_page=reverse_lazy('login')), name='logout'),
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.RaceViewList.as_view(), name='Race'),
    url(r'^Race$', views.RaceViewList.as_view(), name='Race'),
    url(r'^RaceAll$', views.RaceAllList.as_view(), name='RaceAll'),
    url(r'^Race/add$', views.RaceCreate.as_view(), name='RaceCreate'),
    url(r'^Race/update(?P<pk>\d+)/$', views.RaceUpdate.as_view(), name='RaceUpdate'),
    url(r'^Race/delete(?P<pk>\d+)/$', views.RaceDelete.as_view(), name='RaceDelete'),

    url(r'^Car/$', views.CarViewList.as_view(), name='CarList'),
    url(r'^Car/add$', views.CarAdd.as_view(), name='CarAdd'),
    url(r'^Car/update(?P<pk>\d+)/$', views.CarUpdate.as_view(template_name='Avtoregion/update_form.html'),
        name='CarUpdate'),
    url(r'^Car/delete(?P<pk>\d+)/$', views.CarDelete.as_view(), name='CarDelete'),

    url(r'^Product/$', views.ProductViewList.as_view(), name='ProductList'),
    url(r'^Product/add$', views.ProductAdd.as_view(), name='ProductAdd'),
    url(r'^Product/update(?P<pk>\d+)/$', views.ProductUpdate.as_view(template_name='Avtoregion/update_form.html'),
        name='ProductUpdate'),
    url(r'^Product/delete(?P<pk>\d+)/$', views.ProductDelete.as_view(), name='ProductDelete'),

    url(r'^Driver/$', views.DriverViewList.as_view(), name='DriverList'),
    url(r'^Driver/add$', views.DriverAdd.as_view(), name='DriverAdd'),
    url(r'^Driver/update(?P<pk>\d+)/$', views.DriverUpdate.as_view(template_name='Avtoregion/update_form.html'),
        name='DriverUpdate'),
    url(r'^Driver/delete(?P<pk>\d+)/$', views.DriverDelete.as_view(), name='DriverDelete'),

    url(r'^Supplier/$', views.SupplierViewList.as_view(), name='SupplierList'),
    url(r'^Supplier/add$', views.SupplierAdd.as_view(), name='SupplierAdd'),
    url(r'^Supplier/update(?P<pk>\d+)/$', views.SupplierUpdate.as_view(template_name='Avtoregion/update_form.html'),
        name='SupplierUpdate'),
    url(r'^Supplier/delete(?P<pk>\d+)/$', views.SupplierDelete.as_view(), name='SupplierDelete'),

    url(r'^Customer/$', views.CustomerViewList.as_view(), name='CustomerList'),
    url(r'^Customer/add$', views.CustomerAdd.as_view(), name='CustomerAdd'),
    url(r'^Customer/update(?P<pk>\d+)/$', views.CustomerUpdate.as_view(template_name='Avtoregion/update_form.html'),
        name='CustomerUpdate'),
    url(r'^Customer/delete(?P<pk>\d+)/$', views.CustomerDelete.as_view(), name='CustomerDelete'),

    url(r'^Trailer/$', views.TrailerViewList.as_view(), name='TrailerList'),
    url(r'^Trailer/add$', views.TrailerAdd.as_view(), name='TrailerAdd'),
    url(r'^Trailer/update(?P<pk>\d+)/$', views.TrailerUpdate.as_view(template_name='Avtoregion/update_form.html'),
        name='TrailerUpdate'),
    url(r'^Trailer/delete(?P<pk>\d+)/$', views.TrailerDelete.as_view(), name='TrailerDelete'),

    url(r'^Mediator/$', views.MediatorViewList.as_view(), name='MediatorList'),
    url(r'^Mediator/add$', views.MediatorAdd.as_view(), name='MediatorAdd'),
    url(r'^Mediator/update(?P<pk>\d+)/$', views.MediatorUpdate.as_view(template_name='Avtoregion/update_form.html'),
        name='MediatorUpdate'),
    url(r'^Mediator/delete(?P<pk>\d+)/$', views.MediatorDelete.as_view(), name='MediatorDelete'),

    url(r'^Shipment/$', views.ShipmentViewList.as_view(), name='ShipmentList'),
    url(r'^Shipment/add$', views.ShipmentAdd.as_view(), name='ShipmentAdd'),
    url(r'^Shipment/update(?P<pk>\d+)/$', views.ShipmentUpdate.as_view(template_name='Avtoregion/update_form.html'),
        name='ShipmentUpdate'),
    url(r'^Shipment/delete(?P<pk>\d+)/$', views.ShipmentDelete.as_view(), name='ShipmentDelete'),

    url(r'^Supplier/accumulate/$', views.accumulate_sup, name='SupplierAcc'),
    url(r'^Customer/accumulate/$', views.accumulate_cus, name='CustomerAcc'),
    url(r'^Car/accumulate/$', views.accumulate_car, name='CarAcc'),
    url(r'^Driver/accumulate/$', views.accumulate_driver, name='DriverAcc'),

]
