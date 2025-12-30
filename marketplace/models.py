# -*- coding: utf-8 -*-
"""
Created on Sun Dec  7 13:24:43 2025

@author: jvz16
"""

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone

User = settings.AUTH_USER_MODEL


# Países de Hispanoamérica principales (puedes ampliar después)
COUNTRY_CHOICES = [
    ("AR", "Argentina"),
    ("BO", "Bolivia"),
    ("CL", "Chile"),
    ("CO", "Colombia"),
    ("CR", "Costa Rica"),
    ("CU", "Cuba"),
    ("DO", "República Dominicana"),
    ("EC", "Ecuador"),
    ("ES", "España"),
    ("GT", "Guatemala"),
    ("HN", "Honduras"),
    ("MX", "México"),
    ("NI", "Nicaragua"),
    ("PA", "Panamá"),
    ("PE", "Perú"),
    ("PR", "Puerto Rico"),
    ("PY", "Paraguay"),
    ("SV", "El Salvador"),
    ("UY", "Uruguay"),
    ("VE", "Venezuela"),
]

COUNTRY_DIAL_CODES = {
    "AR": "54",
    "BO": "591",
    "CL": "56",
    "CO": "57",
    "CR": "506",
    "CU": "53",
    "DO": "1",
    "EC": "593",
    "ES": "34",
    "GT": "502",
    "HN": "504",
    "MX": "52",
    "NI": "505",
    "PA": "507",
    "PE": "51",
    "PR": "1",
    "PY": "595",
    "SV": "503",
    "UY": "598",
    "VE": "58",
}

CURRENCY_CHOICES = [
    ("CRC", "Colones"),
    ("USD", "Dólares"),
]


def get_country_dial_code(country_code: str) -> str:
    return COUNTRY_DIAL_CODES.get(country_code, "")


class TimestampedModel(models.Model):
    creado = models.DateTimeField(default=timezone.now)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CustomerProfile(TimestampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pais = models.CharField(max_length=2, choices=COUNTRY_CHOICES, default="CR")
    provincia = models.CharField("Provincia / Estado", max_length=100, blank=True)
    canton = models.CharField(max_length=100, blank=True)
    distrito = models.CharField(max_length=100, blank=True)
    telefono_nacional = models.CharField(
        "Teléfono (sin código de país)",
        max_length=20,
        help_text="Escribe el número sin código de país ni signos.",
    )
    notas_estilo = models.TextField(
        blank=True,
        help_text="Tallas, colores preferidos u otras notas.",
    )

    def __str__(self):
        return f"Cliente: {self.user.get_full_name() or self.user.username}"

    @property
    def whatsapp_link(self):
        dial = get_country_dial_code(self.pais)
        if not dial or not self.telefono_nacional:
            return None
        digits = "".join(ch for ch in self.telefono_nacional if ch.isdigit())
        if not digits:
            return None
        return f"https://wa.me/{dial}{digits}"


class ShopperProfile(TimestampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pais = models.CharField(max_length=2, choices=COUNTRY_CHOICES, default="CR")
    provincia = models.CharField("Provincia / Estado", max_length=100, blank=True)
    canton = models.CharField(max_length=100, blank=True)
    distrito = models.CharField(max_length=100, blank=True)

    biografia = models.TextField("Biografía", blank=True)
    # Se almacena como texto separado por comas, pero se maneja como multi-select en los formularios
    especialidades = models.CharField(
        max_length=255,
        blank=True,
        help_text="Ej: ROPA,TECH,NINOS… (se gestiona desde el formulario)",
    )
    ciudad_base = models.CharField(max_length=100, blank=True)
    actualmente_en_el_extranjero = models.BooleanField(default=False)
    ciudad_extranjero = models.CharField(max_length=100, blank=True)
    pais_extranjero = models.CharField(max_length=100, blank=True)
    fecha_regreso = models.DateField(null=True, blank=True)

    # tarifa_base_crc = models.PositiveIntegerField(default=0)

    acepta_pagos_parciales = models.BooleanField(
        default=True,
        verbose_name="Acepta pagos parciales",
    )
    acepta_nuevos_pedidos = models.BooleanField(
        default=True,
        verbose_name="Acepta nuevos pedidos",
    )
    monto_minimo_habitual = models.PositiveIntegerField(
        default=0,
        blank=True,
        verbose_name="Monto mínimo habitual (aprox.)",
    )
    monto_maximo_habitual = models.PositiveIntegerField(
        default=0,
        blank=True,
        verbose_name="Monto máximo habitual (aprox.)",
    )

    esquema_tarifas = models.TextField(
        "Esquema de tarifas",
        blank=True,
        help_text=(
            "Ejemplos: '10% sobre el valor de compra, mínimo 20 USD'; "
            "'tarifa fija por día de compras'; etc."
        ),
    )

    calificacion = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    verificado = models.BooleanField(default=False)
    telefono_nacional = models.CharField(
        "Teléfono (sin código de país)",
        max_length=20,
        help_text="Número de WhatsApp sin código de país.",
    )


    def __str__(self):
        return f"Shopper: {self.user.get_full_name() or self.user.username}"

    @property
    def ubicacion_actual(self):
        if self.actualmente_en_el_extranjero:
            if self.ciudad_extranjero or self.pais_extranjero:
                return f"En {self.ciudad_extranjero or ''} {self.pais_extranjero or ''}".strip()
            return "En el extranjero"
        return self.ciudad_base or "Sin ciudad definida"

    @property
    def whatsapp_link(self):
        dial = get_country_dial_code(self.pais)
        if not dial or not self.telefono_nacional:
            return None
        digits = "".join(ch for ch in self.telefono_nacional if ch.isdigit())
        if not digits:
            return None
        return f"https://wa.me/{dial}{digits}"


class Trip(TimestampedModel):
    shopper = models.ForeignKey(
        ShopperProfile, on_delete=models.CASCADE, related_name="viajes"
    )
    origen = models.CharField(max_length=100, blank=True)
    ciudad_destino = models.CharField(max_length=100)
    pais_destino = models.CharField(max_length=100, blank=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    notas = models.TextField(blank=True)

    def __str__(self):
        return f"Viaje a {self.ciudad_destino} ({self.shopper})"


class Order(TimestampedModel):
    ESTADO_CHOICES = [
        ("NUEVO", "Nuevo"),
        ("BUSCANDO_SHOPPER", "Buscando shopper"),
        ("EN_SELECCION", "En selección"),
        ("COMPRADO", "Comprado"),
        ("EN_TRANSITO", "En tránsito"),
        ("ENTREGADO", "Entregado"),
        ("CANCELADO", "Cancelado"),
    ]

    MODO_PRESUPUESTO_CHOICES = [
        ("POR_ARTICULO", "Presupuesto máximo por artículo"),
        ("TOTAL", "Presupuesto máximo total"),
    ]

    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name="pedidos",
        verbose_name="Cliente",
    )
    shopper = models.ForeignKey(
        ShopperProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pedidos",
        verbose_name="Shopper asignado",
    )
    titulo = models.CharField(
        max_length=200,
        verbose_name="Título del pedido",
        help_text="Ej: Vestido para boda, laptop de trabajo, regalos…",
        blank=True,
        default="",
    )

    # NUEVO: Precio acordado (lo que el shopper define que cuesta el servicio/pedido)
    precio = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Precio",
        help_text="Precio acordado del pedido (en la moneda del pedido).",
    )

    descripcion = models.TextField("Descripción", blank=True)
    modo_presupuesto = models.CharField(
        max_length=20,
        choices=MODO_PRESUPUESTO_CHOICES,
        default="TOTAL",
        verbose_name="Modo de presupuesto",
    )
    moneda = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default="CRC",
        verbose_name="Moneda",
    )
    presupuesto_maximo_por_articulo = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Presupuesto máximo por artículo",
    )
    presupuesto_maximo_total = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Presupuesto máximo total",
    )
    fecha_limite = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha límite",
    )
    estado = models.CharField(
        max_length=30,
        choices=ESTADO_CHOICES,
        default="BUSCANDO_SHOPPER",
    )
    foto_referencia_url = models.URLField(
        "Foto de referencia (URL)", blank=True
    )

    def __str__(self):
        return f"Pedido {self.id} - {self.titulo or 'Sin título'}"

    @property
    def total_pagos(self):
        """
        Pagos aprobados (lo que realmente cuenta en dashboards y saldo).
        """
        return sum(p.monto for p in self.pagos.filter(aprobado=True))

    @property
    def total_pagos_pendientes(self):
        return sum(p.monto for p in self.pagos.filter(aprobado=False))

    @property
    def total_gastos(self):
        return sum(g.monto for g in self.gastos.all())

    @property
    def saldo(self):
        """
        Saldo a cobrar = Precio - Pagos recibidos (aprobados).
        Si no hay precio definido, devuelve 0.
        """
        precio = int(self.precio or 0)
        return precio - int(self.total_pagos or 0)

    @property
    def ganancia(self):
        """
        Ganancia = Pagos recibidos (aprobados) - Gastos
        """
        return int(self.total_pagos or 0) - int(self.total_gastos or 0)


class OrderItem(TimestampedModel):
    CATEGORIA_ARTICULO_CHOICES = [
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

    pedido = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="articulos"
    )
    nombre = models.CharField("Artículo", max_length=200)
    categoria = models.CharField(
        max_length=20, choices=CATEGORIA_ARTICULO_CHOICES
    )
    cantidad = models.PositiveIntegerField(default=1)
    nota = models.CharField("Nota", max_length=255, blank=True)

    # NUEVO: precio por artículo (unitario) definido por el shopper
    precio_unitario = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Precio unitario",
        help_text="Precio por unidad (en la moneda del pedido).",
    )

    def __str__(self):
        return f"{self.nombre} ({self.get_categoria_display()})"



class Payment(TimestampedModel):
    TIPO_PAGO_CHOICES = [
        ("ADELANTO", "Adelanto"),
        ("PARCIAL", "Pago parcial"),
        ("FINAL", "Pago final"),
    ]

    METODO_CHOICES = [
        ("SINPE", "SINPE"),
        ("EFECTIVO", "Efectivo"),
        ("TARJETA", "Tarjeta"),
        ("PAYPAL", "PayPal"),
        ("OTRO", "Otro"),
    ]

    CREADO_POR_CHOICES = [
        ("SHOPPER", "Shopper"),
        ("CLIENTE", "Cliente"),
    ]

    pedido = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="pagos"
    )
    monto = models.PositiveIntegerField("Monto")
    tipo_pago = models.CharField(
        max_length=20, choices=TIPO_PAGO_CHOICES, verbose_name="Tipo de pago"
    )
    metodo = models.CharField(
        max_length=20,
        choices=METODO_CHOICES,
        verbose_name="Método de pago",
    )
    nota = models.CharField("Nota", max_length=255, blank=True)

    # NUEVO: aprobación (para reportes del cliente)
    creado_por = models.CharField(
        max_length=10,
        choices=CREADO_POR_CHOICES,
        default="SHOPPER",
    )
    aprobado = models.BooleanField(default=True)

    def __str__(self):
        estado = "aprobado" if self.aprobado else "pendiente"
        return f"Pago {self.monto} ({self.tipo_pago}) - {estado}"


class Expense(TimestampedModel):
    CATEGORIA_CHOICES = [
        ("PRODUCTO", "Producto"),
        ("ENVIO", "Envío"),
        ("IMPUESTO", "Impuesto"),
        ("VUELO", "Vuelo"),
        ("HOSPEDAJE", "Hospedaje"),
        ("COMIDA", "Comida"),
        ("TRANSPORTE", "Transporte"),
        ("OTRO", "Otro"),
    ]

    pedido = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="gastos",
        null=True,
        blank=True,
        help_text="Déjalo vacío si es un gasto general (no asociado a un pedido).",
    )
    shopper = models.ForeignKey(
        ShopperProfile,
        on_delete=models.CASCADE,
        related_name="gastos",
        null=True,
        blank=True,
    )
    categoria = models.CharField(
        max_length=20, choices=CATEGORIA_CHOICES, verbose_name="Categoría"
    )
    monto = models.PositiveIntegerField("Monto")
    descripcion = models.CharField("Descripción", max_length=255, blank=True)
    moneda = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default="CRC",
        verbose_name="Moneda",
    )

    def __str__(self):
        return f"Gasto {self.categoria} {self.monto} {self.moneda}"


class ShopperPhoto(models.Model):
    shopper = models.OneToOneField(
        "ShopperProfile",
        related_name="photo",
        on_delete=models.CASCADE,
    )
    image = models.ImageField(upload_to="shoppers_fotos/")

    def __str__(self):
        return f"Foto de {self.shopper}"


class Review(TimestampedModel):
    """
    Reseña estilo Uber:
    - 1 a 5 estrellas obligatorias
    - Comentario opcional
    - Vinculada a un pedido entregado
    """
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="review",
    )
    shopper = models.ForeignKey(
        ShopperProfile,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    rating = models.PositiveSmallIntegerField(
        "Calificación",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField("Comentario", blank=True)

    def __str__(self):
        return f"Review {self.rating}★ de {self.customer} a {self.shopper}"


# =========================
# NUEVO: Carrusel dinámico (Admin -> Landing)
# =========================
class CarouselSlide(TimestampedModel):
    """
    Slides del carrusel de "Ejemplos de lo que podés pedir".
    - Imagen subida desde admin
    - Comentario mostrado arriba de cada vista
    """
    image = models.ImageField(upload_to="carousel/")
    comentario = models.CharField(
        max_length=160,
        blank=True,
        default="",
        help_text="Texto corto que se mostrará arriba de la imagen.",
    )
    orden = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ("orden", "-creado")

    def __str__(self):
        label = self.comentario.strip() or "Slide"
        return f"{label[:40]}"


# =========================
# NUEVO: Fondo de la sección hero (Admin -> Landing)
# =========================
class HeroBackground(TimestampedModel):
    """
    Imagen de fondo para la sección principal del landing (copy + CTA).
    - Subida desde admin
    - Se usa la última activa
    """
    image = models.ImageField(upload_to="hero/")
    activo = models.BooleanField(default=True)
    comentario = models.CharField(
        max_length=120,
        blank=True,
        default="",
        help_text="Opcional: etiqueta interna para identificar el fondo.",
    )

    class Meta:
        ordering = ("-creado",)

    def __str__(self):
        return self.comentario.strip() or f"Hero background #{self.pk}"