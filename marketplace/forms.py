# -*- coding: utf-8 -*-
"""
Created on Sun Dec  7 13:27:25 2025

@author: jvz16
"""

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import (
    Order,
    Payment,
    Expense,
    CustomerProfile,
    ShopperProfile,
    Trip,
    COUNTRY_CHOICES,
    CURRENCY_CHOICES,
    OrderItem,
)

User = get_user_model()


class CustomerSignUpForm(UserCreationForm):
    email = forms.EmailField(label="Correo electrónico", required=True)
    pais = forms.ChoiceField(label="País", choices=COUNTRY_CHOICES)
    provincia = forms.CharField(label="Provincia / Estado", required=False)
    canton = forms.CharField(label="Cantón / Ciudad", required=False)
    distrito = forms.CharField(label="Distrito / Barrio", required=False)
    telefono_nacional = forms.CharField(
        label="Teléfono (sin código de país)",
        help_text="Solo números, sin + ni código de país.",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            CustomerProfile.objects.create(
                user=user,
                pais=self.cleaned_data["pais"],
                provincia=self.cleaned_data.get("provincia", ""),
                canton=self.cleaned_data.get("canton", ""),
                distrito=self.cleaned_data.get("distrito", ""),
                telefono_nacional=self.cleaned_data["telefono_nacional"],
            )
        return user


class ShopperSignUpForm(UserCreationForm):
    email = forms.EmailField(label="Correo electrónico", required=True)
    pais = forms.ChoiceField(label="País", choices=COUNTRY_CHOICES)
    provincia = forms.CharField(label="Provincia / Estado", required=False)
    canton = forms.CharField(label="Cantón / Ciudad", required=False)
    distrito = forms.CharField(label="Distrito / Barrio", required=False)
    telefono_nacional = forms.CharField(
        label="Teléfono (sin código de país)",
        help_text="Número de WhatsApp sin código de país.",
    )

    # Dropdown multi-select (no checkboxes)
    especialidades = forms.MultipleChoiceField(
        label="Especialidades de compra",
        required=False,
        choices=OrderItem.CATEGORIA_ARTICULO_CHOICES,
        widget=forms.SelectMultiple(attrs={"class": "form-select", "size": "7"}),
        help_text="Seleccioná los tipos de productos en los que te especializás (podés elegir varios).",
    )

    ciudad_base = forms.CharField(label="Ciudad base", required=False)


    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            especialidades_list = self.cleaned_data.get("especialidades", [])
            ShopperProfile.objects.create(
                user=user,
                pais=self.cleaned_data["pais"],
                provincia=self.cleaned_data.get("provincia", ""),
                canton=self.cleaned_data.get("canton", ""),
                distrito=self.cleaned_data.get("distrito", ""),
                telefono_nacional=self.cleaned_data["telefono_nacional"],
                especialidades=",".join(especialidades_list),
                ciudad_base=self.cleaned_data.get("ciudad_base", "")
            )
        return user


class ShopperProfileForm(forms.ModelForm):
    ESPECIALIDADES_CHOICES = [
        ("ROPA", "Ropa"),
        ("CALZADO", "Calzado"),
        ("TECH", "Tecnología"),
        ("ACCESORIOS", "Accesorios"),
        ("COSMETICOS", "Cosméticos / Belleza"),
        ("HOGAR", "Hogar"),
        ("DEPORTES", "Deportes"),
        ("NINOS", "Niños / Bebés"),
        ("JUGUETES", "Juguetes"),
        ("LUJO", "Lujo"),
        ("OTRO", "Otro"),
    ]

    # Dropdown multi-select (no checkboxes)
    especialidades = forms.MultipleChoiceField(
        choices=ESPECIALIDADES_CHOICES,
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-select", "size": "7"}),
        label="Especialidades de compra",
    )


    foto_archivo = forms.ImageField(
        required=False,
        label="Foto de perfil",
        widget=forms.ClearableFileInput(attrs={"class": "form-control"}),
    )


    # País extranjero: solo USA (y vacío cuando no aplica)
    pais_extranjero = forms.ChoiceField(
        label="País extranjero",
        required=False,
        choices=[("", "—"), ("USA", "USA")],
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    esquema_tarifas = forms.CharField(
        label="Esquema de tarifas",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        help_text=(
            "Ejemplos: '10% sobre el valor de compra, mínimo 20 USD'; "
            "'tarifa fija por día de compras'; etc."
        ),
    )

    class Meta:
        model = ShopperProfile
        fields = [
            # biografia eliminado
            "especialidades",
            "ciudad_base",
            "actualmente_en_el_extranjero",
            "ciudad_extranjero",
            "pais_extranjero",
            "fecha_regreso",
            "acepta_nuevos_pedidos",
            "acepta_pagos_parciales",
            # monto_minimo_habitual eliminado
            # monto_maximo_habitual eliminado
            "tarifa_base_crc",
            "esquema_tarifas",
        ]
        widgets = {
            "ciudad_base": forms.TextInput(attrs={"class": "form-control"}),
            "ciudad_extranjero": forms.TextInput(attrs={"class": "form-control"}),
            "fecha_regreso": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "tarifa_base_crc": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Inicial especialidades desde string CSV
        if self.instance and self.instance.especialidades:
            self.initial["especialidades"] = [
                e.strip()
                for e in self.instance.especialidades.split(",")
                if e.strip()
            ]

        # Asegurar clases bootstrap en selects básicos del ModelForm
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.Select) and "class" not in field.widget.attrs:
                field.widget.attrs["class"] = "form-select"

    def clean_especialidades(self):
        valores = self.cleaned_data.get("especialidades", [])
        return ",".join(valores)


class TripForm(forms.ModelForm):
    """
    Form simple para registrar próximos viajes del shopper.
    Nota: pais_destino se limita a USA para estandarizar y facilitar filtros.
    """
    pais_destino = forms.ChoiceField(
        label="País destino",
        required=False,
        choices=[("USA", "USA")],
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = Trip
        fields = ["ciudad_destino", "pais_destino", "fecha_inicio", "fecha_fin", "notas"]
        widgets = {
            "ciudad_destino": forms.TextInput(attrs={"class": "form-control"}),
            "fecha_inicio": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "fecha_fin": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "notas": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
        }


class OrderForm(forms.ModelForm):
    """
    Importante:
    - NO mostramos título ni modo_presupuesto.
    - El título se autogenera en la vista a partir de los artículos.
    - modo_presupuesto se fija a TOTAL en la vista.
    """
    shopper = forms.ModelChoiceField(
        label="Shopper de preferencia",
        queryset=ShopperProfile.objects.all(),
        required=False,
        help_text="Podés elegir un shopper o dejarlo vacío para que cualquiera lo tome.",
    )
    moneda = forms.ChoiceField(
        label="Moneda",
        choices=CURRENCY_CHOICES,
    )
    foto_referencia_url = forms.URLField(
        label="Foto de referencia (URL)",
        required=False,
        help_text="Opcional: enlace a una foto de referencia del producto.",
    )

    class Meta:
        model = Order
        fields = [
            "presupuesto_maximo_total",
            "moneda",
            "shopper",
            "foto_referencia_url",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Bootstrap look
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault("class", "form-select")
            else:
                field.widget.attrs.setdefault("class", "form-control")

        def label_from_instance(obj):
            nombre = obj.user.get_full_name() or obj.user.username
            return f"{nombre} · ⭐ {obj.calificacion}"

        self.fields["shopper"].label_from_instance = label_from_instance


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["monto", "tipo_pago", "metodo", "nota"]


class ExpenseProductoForm(forms.ModelForm):
    """
    Gastos por producto (pedido).
    No incluye vuelos, hospedaje, etc.
    """

    class Meta:
        model = Expense
        fields = ["categoria", "monto", "descripcion", "moneda"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categorias_permitidas = [
            ("PRODUCTO", "Producto"),
            ("ENVIO", "Envío"),
            ("IMPUESTO", "Impuesto"),
            ("TRANSPORTE", "Transporte"),
            ("OTRO", "Otro"),
        ]
        self.fields["categoria"].choices = categorias_permitidas


class ExpenseGeneralForm(forms.ModelForm):
    """
    Gastos generales del mes (vuelos, hospedaje, comidas, etc.).
    """

    class Meta:
        model = Expense
        fields = ["categoria", "monto", "descripcion", "moneda"]