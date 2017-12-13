# -*- coding: utf-8 -*-

from django.urls import path

from . import views


app_name = 'files'
urlpatterns = [
    path('file/add/<int:content_type>/<int:object_id>/', views.add,
         name='add'),
    path('file/add_another/<int:content_type>/<int:object_id>/',
         views.add_another, name='add_another'),
    path('file/<slug:slug>/', views.detail, name='file'),
    path('file/<slug:slug>/edit/', views.edit, name='edit'),
    path('file/<slug:slug>/delete/', views.delete, name='delete'),
]
