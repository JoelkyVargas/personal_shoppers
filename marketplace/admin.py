# -*- coding: utf-8 -*-
"""
Created on Sun Dec  7 13:27:04 2025

@author: jvz16
"""

from django.contrib import admin
from .models import (
    CustomerProfile,
    ShopperProfile,
    Trip,
    Order,
    Payment,
    Expense,
    CarouselSlide,
    HeroBackground,
)


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "pais",
        "provincia",
        "canton",
        "distrito",
        "telefono_nacional",
        "creado",
    )
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "telefono_nacional",
    )
    list_filter = ("pais", "provincia", "creado")


@admin.register(ShopperProfile)
class ShopperProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "pais",
        "ciudad_base",
        "actualmente_en_el_extranjero",
        "pais_extranjero",
        "calificacion",
        "verificado",
        "telefono_nacional",
        "creado",
    )
    search_fields = ("user__username", "user__first_name", "user__last_name")
    list_filter = ("pais", "actualmente_en_el_extranjero", "verificado")


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = (
        "shopper",
        "origen",
        "ciudad_destino",
        "pais_destino",
        "fecha_inicio",
        "fecha_fin",
    )
    list_filter = ("pais_destino", "fecha_inicio", "fecha_fin")
    search_fields = (
        "shopper__user__username",
        "origen",
        "ciudad_destino",
        "pais_destino",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "titulo",
        "customer",
        "shopper",
        "estado",
        "moneda",
        "fecha_limite",
        "creado",
    )
    list_filter = ("estado", "moneda", "creado")
    search_fields = (
        "titulo",
        "customer__user__username",
        "shopper__user__username",
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "pedido",
        "monto",
        "tipo_pago",
        "metodo",
        "creado_por",
        "aprobado",
        "creado",
    )
    list_filter = ("tipo_pago", "metodo", "creado_por", "aprobado", "creado")
    search_fields = ("pedido__titulo", "pedido__customer__user__username")


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        "pedido",
        "shopper",
        "categoria",
        "monto",
        "moneda",
        "creado",
    )
    list_filter = ("categoria", "moneda", "creado")
    search_fields = ("pedido__titulo", "shopper__user__username", "descripcion")


@admin.register(CarouselSlide)
class CarouselSlideAdmin(admin.ModelAdmin):
    list_display = ("id", "comentario", "orden", "activo", "creado")
    list_filter = ("activo",)
    search_fields = ("comentario",)
    ordering = ("orden", "-creado")


@admin.register(HeroBackground)
class HeroBackgroundAdmin(admin.ModelAdmin):
    list_display = ("id", "comentario", "activo", "creado")
    list_filter = ("activo",)
    search_fields = ("comentario",)
    ordering = ("-creado",)
