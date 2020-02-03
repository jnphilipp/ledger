# -*- coding: utf-8 -*-

from django.urls import path

from .views import invoice, statement


app_name = 'files'
urlpatterns = [
    path('invoice/<slug:slug>', invoice.DetailView.as_view(),
         name='invoice_detail'),
    path('invoice/<int:entry>/create/', invoice.CreateView.as_view(),
         name='invoice_create'),
    path('invoice/<slug:slug>/delete/', invoice.DeleteView.as_view(),
         name='invoice_delete'),
    path('invoice/<slug:slug>/edit/', invoice.UpdateView.as_view(),
         name='invoice_edit'),

    path('statement/', statement.ListView.as_view(), name='statement_list'),
    path('statement/create/', statement.CreateView.as_view(),
         name='statement_create'),
    path('statement/create/<slug:slug>', statement.CreateView.as_view(),
         name='statement_create'),
    path('statement/<slug:slug>', statement.DetailView.as_view(),
         name='statement_detail'),
    path('statement/<slug:slug>/delete/', statement.DeleteView.as_view(),
         name='statement_delete'),
    path('statement/<slug:slug>/edit/', statement.UpdateView.as_view(),
         name='statement_edit'),
]
