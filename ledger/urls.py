# -*- coding: utf-8 -*-
"""ledger URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from accounts.views.entry import ListView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import RedirectView

from . import views


admin.site.site_header = _('ledger administration')


urlpatterns = [
    path('', ListView.as_view(), name='dashboard'),
    path('', ListView.as_view(), name='entry_list'),
    path('<int:page>/', ListView.as_view()),

    path('add/another/success/', views.AnotherSuccessView.as_view(),
         name='create_another_success'),

    path('accounts/', include('accounts.urls')),
    path('categories/', include('categories.urls')),
    path('files/', include('files.urls')),
    path('units/', include('units.urls')),
    path('users/', include('users.urls')),

    path('admin/', admin.site.urls),
    path('favicon.ico', RedirectView.as_view(url='/static/images/logo.png')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
