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
    url(r'^Race/add$', views.RaceCreate.as_view(), name='RaceCreate'),
    url(r'^Race/update$', views.RaceUpdate.as_view(), name='RaceUpdate'),
    url(r'^Race/delete$', views.RaceDelete.as_view(), name='RaceDelete'),

    url(r'^Car$', views.CarView, name='Car'),
    url(r'^Car/update$', views.CarUpdate.as_view(), name='CarUpdate'),
    url(r'^Car/delete$', views.CarDelete.as_view(), name='CarDelete'),

    url(r'^Product$', views.ProductView, name='Product'),
    url(r'^Product/update$', views.ProductUpdate.as_view(), name='ProductUpdate'),
    url(r'^Product/delete$', views.ProductDelete.as_view(), name='ProductDelete'),

    url(r'^Driver$', views.DriverView, name='Driver'),
    url(r'^Driver/update$', views.DriverUpdate.as_view(), name='DriverUpdate'),
    url(r'^Driver/delete$', views.DriverDelete.as_view(), name='DriverDelete'),

    url(r'^Supplier$', views.SupplierView, name='Supplier'),
    url(r'^Supplier/update$', views.SupplierUpdate.as_view(), name='SupplierUpdate'),
    url(r'^Supplier/delete$', views.SupplierDelete.as_view(), name='SupplierDelete'),

    url(r'^Customer$', views.CustomerView, name='Customer'),
    url(r'^Customer/update$', views.CustomerUpdate.as_view(), name='CustomerUpdate'),
    url(r'^Customer/delete$', views.CustomerDelete.as_view(), name='CustomerDelete'),

    url(r'^Trailer$', views.TrailerView, name='Trailer'),
    url(r'^Trailer/update$', views.TrailerUpdate.as_view(), name='TrailerUpdate'),
    url(r'^Trailer/delete$', views.TrailerDelete.as_view(), name='TrailerDelete'),

    url(r'^Mediator$', views.MediatorView, name='Mediator'),
    url(r'^Mediator/update$', views.MediatorUpdate.as_view(), name='MediatorUpdate'),
    url(r'^Mediator/delete$', views.MediatorDelete.as_view(), name='MediatorDelete'),

    url(r'^Shipment$', views.ShipmentView, name='Shipment'),
    url(r'^Shipment/update$', views.ShipmentUpdate.as_view(), name='ShipmentUpdate'),
    url(r'^Shipment/delete$', views.ShipmentDelete.as_view(), name='ShipmentDelete'),

    url(r'^Supplier/accumulate$', views.SupplierView, name='SupplierAcc'),
]
