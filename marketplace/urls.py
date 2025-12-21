# -*- coding: utf-8 -*-
"""
Created on Sun Dec  7 13:27:25 2025

@author: jvz16
"""


# marketplace/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views

from marketplace import views as marketplace_views

urlpatterns = [
    # Auth
    path("login/", marketplace_views.RoleBasedLoginView.as_view(), name="login"),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="home"),
        name="logout",
    ),

    # Landing / info
    path("", marketplace_views.home, name="home"),
    path("shoppers/", marketplace_views.buscar_shoppers, name="buscar_shoppers"),
    path("como-funciona/", marketplace_views.como_funciona, name="como_funciona"),
    path("faqs/", marketplace_views.faqs, name="faqs"),

    # Detalle de shopper
    path("shoppers/<int:pk>/", marketplace_views.shopper_detail, name="shopper_detail"),

    # Registro
    path("registrarme/cliente/", marketplace_views.register_customer, name="register_customer"),
    path("registrarme/shopper/", marketplace_views.register_shopper, name="register_shopper"),

    # Dashboards
    path("dashboard/shopper/", marketplace_views.shopper_dashboard, name="shopper_dashboard"),
    path("dashboard/cliente/", marketplace_views.customer_dashboard, name="customer_dashboard"),

    # Pedidos
    path("pedidos/nuevo/", marketplace_views.create_order, name="create_order"),

    # Detalle de pedido (cliente)
    path("dashboard/pedidos/<int:pk>/", marketplace_views.order_detail, name="order_detail"),

    # Detalle de pedido (solo shopper)
    path(
        "dashboard/shopper/pedidos/<int:pk>/",
        marketplace_views.shopper_order_detail,
        name="shopper_order_detail",
    ),

    # NUEVO: Preview del pedido antes de tomarlo (solo shopper)
    path(
        "dashboard/shopper/pedidos/<int:pk>/preview/",
        marketplace_views.shopper_order_preview,
        name="shopper_order_preview",
    ),

    path(
        "dashboard/shopper/pedidos/<int:pk>/tomar/",
        marketplace_views.shopper_tomar_pedido,
        name="shopper_tomar_pedido",
    ),
    path(
        "dashboard/shopper/pedidos/<int:pk>/estado/",
        marketplace_views.shopper_update_order_status,
        name="shopper_update_order_status",
    ),

    # Gastos shopper
    path(
        "dashboard/shopper/gastos-generales/",
        marketplace_views.shopper_gastos_generales,
        name="shopper_gastos_generales",
    ),

    # Mi perfil
    path("mi-perfil/", marketplace_views.mi_perfil, name="mi_perfil"),
]
