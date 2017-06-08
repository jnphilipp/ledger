# -*- coding: utf-8 -*-

"""ledger URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
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
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import RedirectView
from ledger import views

admin.site.site_header = 'ledger administration'


urlpatterns = [
    url(r'^$', views.dashboard, name='dashboard'),

    url(r'^accounts/', include('accounts.urls', 'accounts')),
    url(r'^categories/', include('categories.urls', 'categories')),
    url(r'^units/', include('units.urls', 'units')),
    url(r'^users/', include('users.urls', 'users')),

    url(r'^admin/', admin.site.urls),
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/images/logo.png')),
]
