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
    url(r'^login/$', views.LoginViewMix.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(next_page=reverse_lazy('login')), name='logout'),
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.RaceViewList.as_view(), name='Race'),
    url(r'^Constants$', views.ConstantsViewList.as_view(), name='Constants'),
    url(r'^Race$', views.RaceViewList.as_view(), name='Race'),
    url(r'^Race/add$', views.RaceCreate.as_view(), name='RaceCreate'),
    url(r'^Race/add/ajax_track', views.ajax_track, name='RaceAjaxTrack'),
    url(r'^Race/add/ajax_sup', views.ajax_sup, name='RaceAjaxSup'),
    url(r'^Race/add/get_unload_place', views.get_unload_place, name='RaceAjaxCus'),
    url(r'^Race/update/ajax', views.AjaxUpdateState.as_view(), name='RaceUpdateAjax'),
    url(r'^Race/packing/ajax', views.PackingView.as_view(), name='PackAjax'),
    url(r'^Race/way/ajax', views.WayView.as_view(), name='WayAjax'),
    url(r'^Race/update(?P<pk>\d+)/$', views.RaceUpdate.as_view(), name='RaceUpdate'),
    url(r'^Race/delete/$', views.RaceDelete.as_view(), name='RaceDelete'),

    url(r'^Car/$', views.CarViewList.as_view(), name='CarList'),
    url(r'^Car/add$', views.CarAdd.as_view(), name='CarAdd'),
    url(r'^Car/update(?P<pk>\d+)/$', views.CarUpdate.as_view(),
        name='CarUpdate'),
    url(r'^Car/delete/$', views.CarDelete.as_view(), name='CarDelete'),

    url(r'^Unit/$', views.UnitsViewList.as_view(), name='UnitList'),
    url(r'^Unit/add$', views.UnitAdd.as_view(), name='UnitAdd'),
    url(r'^Unit/update(?P<pk>\d+)/$', views.UnitUpdate.as_view(),
        name='UnitUpdate'),
    url(r'^Unit/delete/$', views.UnitDelete.as_view(), name='UnitDelete'),

    url(r'^Product/$', views.ProductViewList.as_view(), name='ProductList'),
    url(r'^Product/add$', views.ProductAdd.as_view(), name='ProductAdd'),
    url(r'^Product/update(?P<pk>\d+)/$', views.ProductUpdate.as_view(template_name='Avtoregion/update_form.html'),
        name='ProductUpdate'),
    url(r'^Product/delete/$', views.ProductDelete.as_view(), name='ProductDelete'),

    url(r'^Driver/$', views.DriverViewList.as_view(), name='DriverList'),
    url(r'^Driver/add$', views.DriverAdd.as_view(), name='DriverAdd'),
    url(r'^Driver/update(?P<pk>\d+)/$', views.DriverUpdate.as_view(template_name='Avtoregion/update_form.html'),
        name='DriverUpdate'),
    url(r'^Driver/delete/$', views.DriverDelete.as_view(), name='DriverDelete'),

    url(r'^Supplier/$', views.SupplierViewList.as_view(), name='SupplierList'),
    url(r'^Supplier/add$', views.SupplierAdd.as_view(), name='SupplierAdd'),
    url(r'^Supplier/update(?P<pk>\d+)/$', views.SupplierUpdate.as_view(template_name='Avtoregion/update_form.html'),
        name='SupplierUpdate'),
    url(r'^Supplier/delete/$', views.SupplierDelete.as_view(), name='SupplierDelete'),
    url(r'^Supplier/load_place/$', views.LoadPlaceViewList.as_view(), name='LoadPlaceList'),
    url(r'^Supplier/load_place/add$', views.LoadAdd.as_view(), name='LoadAdd'),
    url(r'^Supplier/load_place/update(?P<pk>\d+)/$',
        views.LoadUpdate.as_view(template_name='Avtoregion/update_form.html'), name='LoadUpdate'),

    url(r'^Customer/$', views.CustomerViewList.as_view(), name='CustomerList'),
    url(r'^Customer/add$', views.CustomerAdd.as_view(), name='CustomerAdd'),
    url(r'^Customer/update(?P<pk>\d+)/$', views.CustomerUpdate.as_view(template_name='Avtoregion/update_form.html'),
        name='CustomerUpdate'),
    url(r'^Customer/delete/$', views.CustomerDelete.as_view(), name='CustomerDelete'),
    url(r'^Customer/unload_place/$', views.ShipmentViewList.as_view(), name='ShipmentList'),
    url(r'^Customer/unload_place/add$', views.ShipmentAdd.as_view(), name='ShipmentAdd'),
    url(r'^Customer/unload_place/update(?P<pk>\d+)/$',
        views.ShipmentUpdate.as_view(template_name='Avtoregion/update_form.html'), name='ShipmentUpdate'),

    url(r'^Trailer/$', views.TrailerViewList.as_view(), name='TrailerList'),
    url(r'^Trailer/add$', views.TrailerAdd.as_view(), name='TrailerAdd'),
    url(r'^Trailer/update(?P<pk>\d+)/$', views.TrailerUpdate.as_view(template_name='Avtoregion/update_form.html'),
        name='TrailerUpdate'),
    url(r'^Trailer/delete/$', views.TrailerDelete.as_view(), name='TrailerDelete'),

    url(r'^Mediator/$', views.MediatorViewList.as_view(), name='MediatorList'),
    url(r'^Mediator/add$', views.MediatorAdd.as_view(), name='MediatorAdd'),
    url(r'^Mediator/update(?P<pk>\d+)/$', views.MediatorUpdate.as_view(template_name='Avtoregion/update_form.html'),
        name='MediatorUpdate'),
    url(r'^Mediator/delete/$', views.MediatorDelete.as_view(), name='MediatorDelete'),


    url(r'^Accumulate/$', views.Accumulate.as_view(), name='Acc'),
    url(r'^Accumulate/Excel$', views.save_excel, name='AccExcel'),
    url(r'^Car/accumulate/$', views.CarResponce.as_view(), name='CarAcc'),
    url(r'^Driver/accumulate/$', views.DriverResponce.as_view(), name='DriverAcc'),

]
