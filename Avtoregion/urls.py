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
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.RaceView, name='Race'),
    url(r'^Race$', views.RaceView, name='Race'),
    url(r'^RaceAll$', views.RaceAll, name='Race'),
    url(r'^Race/add$', views.RaceCreate.as_view(), name='RaceCreate'),
    url(r'^Race/update$', views.RaceUpdate, name='RaceUpdate'),
    url(r'^Race/delete(?P<pk>\d+)/$', views.RaceDelete.as_view(), name='RaceDelete'),

    url(r'^Car/$', views.CarView, name='Car'),
    url(r'^Car/update(?P<pk>\d+)/$', views.CarUpdate.as_view(template_name='Avtoregion/update_form.html'),
        name='CarUpdate'),
    url(r'^Car/delete(?P<pk>\d+)/$', views.CarDelete.as_view(), name='CarDelete'),

    url(r'^Product/$', views.ProductView, name='Product'),
    url(r'^Product/update(?P<pk>\d+)/$', views.ProductUpdate.as_view(template_name='Avtoregion/update_form.html'),
        name='ProductUpdate'),
    url(r'^Product/delete(?P<pk>\d+)/$', views.ProductDelete.as_view(), name='ProductDelete'),

    url(r'^Driver/$', views.DriverView, name='Driver'),
    url(r'^Driver/update(?P<pk>\d+)/$', views.DriverUpdate.as_view(template_name='Avtoregion/update_form.html'),
        name='DriverUpdate'),
    url(r'^Driver/delete(?P<pk>\d+)/$', views.DriverDelete.as_view(), name='DriverDelete'),

    url(r'^Supplier/$', views.SupplierView, name='Supplier'),
    url(r'^Supplier/update(?P<pk>\d+)/$', views.SupplierUpdate.as_view(template_name='Avtoregion/update_form.html'),
        name='SupplierUpdate'),
    url(r'^Supplier/delete(?P<pk>\d+)/$', views.SupplierDelete.as_view(), name='SupplierDelete'),

    url(r'^Customer/$', views.CustomerView, name='Customer'),
    url(r'^Customer/update(?P<pk>\d+)/$', views.CustomerUpdate.as_view(template_name='Avtoregion/update_form.html'),
        name='CustomerUpdate'),
    url(r'^Customer/delete(?P<pk>\d+)/$', views.CustomerDelete.as_view(), name='CustomerDelete'),

    url(r'^Trailer/$', views.TrailerView, name='Trailer'),
    url(r'^Trailer/update(?P<pk>\d+)/$', views.TrailerUpdate.as_view(template_name='Avtoregion/update_form.html'),
        name='TrailerUpdate'),
    url(r'^Trailer/delete(?P<pk>\d+)/$', views.TrailerDelete.as_view(), name='TrailerDelete'),

    url(r'^Mediator/$', views.MediatorView, name='Mediator'),
    url(r'^Mediator/update(?P<pk>\d+)/$', views.MediatorUpdate.as_view(template_name='Avtoregion/update_form.html'),
        name='MediatorUpdate'),
    url(r'^Mediator/delete(?P<pk>\d+)/$', views.MediatorDelete.as_view(), name='MediatorDelete'),

    url(r'^Shipment/$', views.ShipmentView, name='Shipment'),
    url(r'^Shipment/update(?P<pk>\d+)/$', views.ShipmentUpdate.as_view(template_name='Avtoregion/update_form.html'),
        name='ShipmentUpdate'),
    url(r'^Shipment/delete(?P<pk>\d+)/$', views.ShipmentDelete.as_view(), name='ShipmentDelete'),

    url(r'^Supplier/accumulate/$', views.AccumulateSup, name='SupplierAcc'),
    url(r'^Customer/accumulate/$', views.AccumulateCus, name='CustomerAcc'),
    url(r'^Car/accumulate/$', views.AccumulateCar, name='CarAcc'),
    url(r'^Driver/accumulate/$', views.AccumulateDriver, name='DriverAcc'),
]
