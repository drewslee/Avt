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
    url(r'^Driver$', views.DriverView, name='Driver'),
    url(r'^Supplier$', views.SupplierView, name='Supplier'),
    url(r'^Customer$', views.CustomerView, name='Customer'),
    url(r'^Trailer$', views.TrailerView, name='Trailer'),
    url(r'^Trailer/update$', views.TrailerUpdate.as_view(), name='TrailerUpdate'),
    url(r'^Trailer/delete$', views.TrailerDelete.as_view(), name='TrailerDelete'),
    url(r'^Mediator$', views.MediatorView, name='Mediator'),
    url(r'^Shipment$', views.MediatorView, name='Shipment'),
]
