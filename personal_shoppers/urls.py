# -*- coding: utf-8 -*-
"""
Created on Sun Dec  7 13:24:21 2025

@author: jvz16
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # Rutas de la app principal
    path("", include("marketplace.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
