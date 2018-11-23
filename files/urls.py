# -*- coding: utf-8 -*-

from django.urls import path

from . import views


app_name = 'files'
urlpatterns = [
    path('add/another/<int:content_type>/<int:object_id>/',
         views.CreateView.as_view(), name='create_another'),
    path('add/<int:content_type>/<int:object_id>/', views.CreateView.as_view(),
         name='create'),
    path('<slug:slug>/', views.DetailView.as_view(), name='detail'),
    path('<slug:slug>/edit/', views.UpdateView.as_view(), name='edit'),
    path('<slug:slug>/delete/', views.DeleteView.as_view(), name='delete'),
]
