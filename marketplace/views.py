# -*- coding: utf-8 -*-
"""
Created on Sun Dec  7 13:27:58 2025

@author: jvz16
"""

from datetime import timedelta

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import Sum, Count, Avg, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .models import (
    ShopperProfile,
    CustomerProfile,
    Order,
    Payment,
    Expense,
    OrderItem,
    ShopperPhoto,
    Review,
    Trip,
    CarouselSlide,
    HeroBackground,
    CURRENCY_CHOICES,
)
from .forms import (
    OrderForm,
    PaymentForm,
    ExpenseProductoForm,
    ExpenseGeneralForm,
    CustomerSignUpForm,
    ShopperSignUpForm,
    ShopperProfileForm,
)


class RoleBasedLoginView(LoginView):
    template_name = "marketplace/auth_login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        if ShopperProfile.objects.filter(user=user).exists():
            return reverse("shopper_dashboard")
        if CustomerProfile.objects.filter(user=user).exists():
            return reverse("customer_dashboard")
        return reverse("home")


def get_top_shoppers_for_customer(customer_profile, limit=5):
    qs = ShopperProfile.objects.filter(acepta_nuevos_pedidos=True)

    pais = getattr(customer_profile, "pais", None)
    provincia = getattr(customer_profile, "provincia", None)
    canton = getattr(customer_profile, "canton", None)
    distrito = getattr(customer_profile, "distrito", None)

    if pais:
        qs = qs.filter(pais=pais)
    if provincia:
        qs = qs.filter(provincia=provincia)
    if canton:
        qs = qs.filter(canton=canton)
    if distrito:
        qs = qs.filter(distrito=distrito)

    qs = qs.annotate(
        pedidos_completados_count=Count("pedidos")
    ).order_by("-calificacion", "-pedidos_completados_count")

    return qs[:limit]


def _chunk_list(items, size=2):
    items = list(items)
    return [items[i : i + size] for i in range(0, len(items), size)]


def home(request):
    es_cliente = False
    es_shopper = False
    if request.user.is_authenticated:
        es_cliente = CustomerProfile.objects.filter(user=request.user).exists()
        es_shopper = ShopperProfile.objects.filter(user=request.user).exists()

    shoppers_qs = ShopperProfile.objects.all()

    shoppers = []
    if not es_shopper:
        shoppers = shoppers_qs.order_by("-calificacion", "-creado")[:6]

    en_usa_qs = ShopperProfile.objects.filter(
        actualmente_en_el_extranjero=True
    ).filter(
        Q(pais_extranjero__icontains="usa")
        | Q(pais_extranjero__icontains="estados unidos")
        | Q(pais_extranjero__icontains="united states")
        | Q(pais_extranjero__icontains="eeuu")
    ).order_by("-calificacion", "-actualizado", "-creado")

    en_usa_ahora = list(en_usa_qs)
    en_usa_slides = _chunk_list(en_usa_ahora, size=2)

    hoy = timezone.now().date()
    limite = hoy + timedelta(days=7)

    trips_qs = Trip.objects.filter(
        fecha_inicio__gte=hoy,
        fecha_inicio__lte=limite,
    ).filter(
        Q(pais_destino__icontains="usa")
        | Q(pais_destino__icontains="estados unidos")
        | Q(pais_destino__icontains="united states")
        | Q(pais_destino__icontains="eeuu")
    ).select_related("shopper").order_by("fecha_inicio", "-shopper__calificacion")

    seen = set()
    viajan_pronto_items = []
    for t in trips_qs:
        if t.shopper_id in seen:
            continue
        seen.add(t.shopper_id)
        viajan_pronto_items.append({"shopper": t.shopper, "trip": t})

    viajan_pronto_slides = _chunk_list(viajan_pronto_items, size=2)

    stats_shoppers = shoppers_qs.count()
    stats_orders = Order.objects.filter(estado="ENTREGADO").count()
    avg_rating_raw = Review.objects.aggregate(avg=Avg("rating"))["avg"] or 0
    stats_rating = round(float(avg_rating_raw), 1) if avg_rating_raw else 0.0

    carousel_slides = CarouselSlide.objects.filter(activo=True).order_by("orden", "-creado")


    # NUEVO: fondo del hero (último activo)
    hero_bg = HeroBackground.objects.filter(activo=True).order_by("-creado").first()


    context = {
        "shoppers": shoppers,
        "es_cliente": es_cliente,
        "es_shopper": es_shopper,
        "stats_shoppers": stats_shoppers,
        "stats_orders": stats_orders,
        "stats_rating": stats_rating,
        "en_usa_ahora": en_usa_ahora,
        "en_usa_slides": en_usa_slides,
        "viajan_pronto_items": viajan_pronto_items,
        "viajan_pronto_slides": viajan_pronto_slides,
        "carousel_slides": carousel_slides,
        "hero_bg": hero_bg,
    }
    return render(request, "marketplace/home.html", context)


def shopper_detail(request, pk):
    shopper = get_object_or_404(ShopperProfile, pk=pk)
    pedidos_atendidos = shopper.pedidos.count()
    return render(
        request,
        "marketplace/shopper_detail.html",
        {"shopper": shopper, "pedidos_atendidos": pedidos_atendidos},
    )


def register_customer(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = CustomerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("customer_dashboard")
    else:
        form = CustomerSignUpForm()

    return render(request, "marketplace/auth_register_customer.html", {"form": form})


def register_shopper(request):
    if request.user.is_authenticated:
        return redirect("home")

    foto_error = None

    if request.method == "POST":
        data = request.POST.copy()


        form = ShopperSignUpForm(data)
        foto_file = request.FILES.get("foto_archivo")

        if not foto_file:
            foto_error = "Subir una foto es obligatorio para registrarte como shopper."

        if form.is_valid() and not foto_error:
            user = form.save()
            login(request, user)

            shopper_profile = ShopperProfile.objects.get(user=user)

            ShopperPhoto.objects.update_or_create(
                shopper=shopper_profile,
                defaults={"image": foto_file},
            )

            return redirect("shopper_dashboard")
    else:
        form = ShopperSignUpForm()

    return render(
        request,
        "marketplace/auth_register_shopper.html",
        {
            "form": form,
            "foto_error": foto_error,
        },
    )


@login_required
def mi_perfil(request):
    shopper_profile = None
    try:
        shopper_profile = ShopperProfile.objects.get(user=request.user)
    except ShopperProfile.DoesNotExist:
        shopper_profile = None

    if shopper_profile:
        from .forms import TripForm

        profile_form = ShopperProfileForm(instance=shopper_profile)
        trip_form = TripForm()

        if request.method == "POST":
            form_type = (request.POST.get("form_type") or "").strip().lower()
            es_profile_post = (form_type == "profile") or ("guardar_perfil" in request.POST)
            es_trip_post = (form_type == "trip") or ("agregar_viaje" in request.POST)

            if es_profile_post:
                # IMPORTANTÍSIMO: incluir request.FILES (aunque no subas foto, esto es correcto)
                profile_form = ShopperProfileForm(request.POST, request.FILES, instance=shopper_profile)
                if profile_form.is_valid():
                    profile_form.save()

                    foto_file = request.FILES.get("foto_archivo")
                    if foto_file:
                        ShopperPhoto.objects.update_or_create(
                            shopper=shopper_profile,
                            defaults={"image": foto_file},
                        )
                    return redirect("mi_perfil")

            elif es_trip_post:
                trip_form = TripForm(request.POST)
                if trip_form.is_valid():
                    trip = trip_form.save(commit=False)
                    trip.shopper = shopper_profile
                    trip.save()
                    return redirect("mi_perfil")

        hoy = timezone.now().date()
        viajes_futuros = shopper_profile.viajes.filter(fecha_inicio__gte=hoy).order_by("fecha_inicio")
        viajes_pasados = shopper_profile.viajes.filter(fecha_fin__lt=hoy).order_by("-fecha_fin")

        pedidos_completados = shopper_profile.pedidos.filter(estado="ENTREGADO").count()

        # ===== CLAVE: calcular foto_url y pasarlo al template =====
        foto_url = None
        if hasattr(shopper_profile, "photo") and getattr(shopper_profile.photo, "image", None):
            try:
                foto_url = shopper_profile.photo.image.url
            except Exception:
                foto_url = None

        context = {
            "shopper": shopper_profile,
            "form": profile_form,
            "trip_form": trip_form,
            "viajes_futuros": viajes_futuros,
            "viajes_pasados": viajes_pasados,
            "pedidos_completados": pedidos_completados,
            "foto_url": foto_url,  # <-- ESTO ARREGLA EL REQUIRED FALSO
        }
        return render(request, "marketplace/shopper_profile.html", context)

    try:
        CustomerProfile.objects.get(user=request.user)
        return redirect("customer_dashboard")
    except CustomerProfile.DoesNotExist:
        pass

    return redirect("home")



@login_required
def shopper_dashboard(request):
    shopper_profile = get_object_or_404(ShopperProfile, user=request.user)

    pedidos = (
        shopper_profile.pedidos.select_related("customer")
        .prefetch_related("pagos", "gastos", "articulos")
        .order_by("-creado")
    )

    total_ingresos = (
        Payment.objects.filter(pedido__shopper=shopper_profile, aprobado=True)
        .aggregate(total=Sum("monto"))["total"]
        or 0
    )

    gastos_generales = (
        Expense.objects.filter(shopper=shopper_profile, pedido__isnull=True)
        .aggregate(total=Sum("monto"))["total"]
        or 0
    )

    gastos_por_pedido = (
        Expense.objects.filter(shopper=shopper_profile, pedido__isnull=False)
        .aggregate(total=Sum("monto"))["total"]
        or 0
    )

    ganancia_neta = total_ingresos - gastos_generales - gastos_por_pedido

    pedidos_abiertos = Order.objects.filter(
        shopper__isnull=True, estado="BUSCANDO_SHOPPER"
    ).select_related("customer").prefetch_related("articulos").order_by("-creado")

    context = {
        "shopper": shopper_profile,
        "pedidos": pedidos,
        "total_ingresos": total_ingresos,
        "gastos_generales": gastos_generales,
        "gastos_por_pedido": gastos_por_pedido,
        "ganancia_neta": ganancia_neta,
        "pedidos_abiertos": pedidos_abiertos,
        "pedidos_abiertos_count": pedidos_abiertos.count(),
    }
    return render(request, "marketplace/shopper_dashboard.html", context)


@login_required
def shopper_order_preview(request, pk):
    """
    Ver un pedido ABIERTO antes de tomarlo (solo shoppers).
    """
    shopper_profile = get_object_or_404(ShopperProfile, user=request.user)
    pedido = get_object_or_404(
        Order,
        pk=pk,
        shopper__isnull=True,
        estado="BUSCANDO_SHOPPER",
    )

    cliente = pedido.customer
    whatsapp_cliente = cliente.whatsapp_link

    ubicacion_cliente = " · ".join(
        [x for x in [cliente.distrito, cliente.canton, cliente.provincia, cliente.get_pais_display()] if x]
    ).strip()

    return render(
        request,
        "marketplace/shopper_order_preview.html",
        {
            "shopper": shopper_profile,
            "pedido": pedido,
            "cliente": cliente,
            "whatsapp_cliente": whatsapp_cliente,
            "ubicacion_cliente": ubicacion_cliente,
        },
    )


@login_required
def shopper_update_order_status(request, pk):
    shopper_profile = get_object_or_404(ShopperProfile, user=request.user)
    pedido = get_object_or_404(Order, pk=pk, shopper=shopper_profile)

    if request.method == "POST":
        new_status = request.POST.get("estado")
        allowed_status = ["EN_SELECCION", "COMPRADO", "EN_TRANSITO", "ENTREGADO", "CANCELADO"]
        if new_status in allowed_status:
            pedido.estado = new_status
            pedido.save()
        return redirect("shopper_order_detail", pk=pedido.pk)

    return redirect("shopper_order_detail", pk=pedido.pk)


@login_required
def shopper_tomar_pedido(request, pk):
    shopper_profile = get_object_or_404(ShopperProfile, user=request.user)
    pedido = get_object_or_404(
        Order,
        pk=pk,
        shopper__isnull=True,
        estado="BUSCANDO_SHOPPER",
    )
    pedido.shopper = shopper_profile
    pedido.estado = "EN_SELECCION"
    pedido.save()
    return redirect("shopper_dashboard")


@login_required
def shopper_order_detail(request, pk):
    shopper_profile = get_object_or_404(ShopperProfile, user=request.user)
    pedido = get_object_or_404(Order, pk=pk, shopper=shopper_profile)

    pago_form = PaymentForm()
    gasto_form = ExpenseProductoForm()

    if request.method == "POST":
        # Cambiar estado desde dropdown (en el detalle)
        if "guardar_estado" in request.POST:
            new_status = request.POST.get("estado")
            allowed_status = ["EN_SELECCION", "COMPRADO", "EN_TRANSITO", "ENTREGADO", "CANCELADO"]
            if new_status in allowed_status:
                pedido.estado = new_status
                pedido.save()
            return redirect("shopper_order_detail", pk=pedido.pk)

        # Guardar precio del pedido (si lo seguís usando)
        if "guardar_precio" in request.POST:
            precio_raw = (request.POST.get("precio") or "").strip()
            if precio_raw.isdigit():
                pedido.precio = int(precio_raw)
                pedido.save()
            return redirect("shopper_order_detail", pk=pedido.pk)

        # NUEVO: Guardar precio unitario por artículo
        if "guardar_precio_articulo" in request.POST:
            item_id = request.POST.get("item_id")
            precio_raw = (request.POST.get("precio_unitario") or "").strip()

            art = get_object_or_404(OrderItem, pk=item_id, pedido=pedido)
            if precio_raw.isdigit():
                art.precio_unitario = int(precio_raw)
                art.save()
            else:
                # permitir limpiar si viene vacío
                if precio_raw == "":
                    art.precio_unitario = None
                    art.save()
            return redirect("shopper_order_detail", pk=pedido.pk)

        # NUEVO: Editar monto de un gasto ya creado (línea completa)
        if "editar_gasto_pedido" in request.POST:
            gasto_id = request.POST.get("gasto_id")
            monto_raw = (request.POST.get("monto") or "").strip()

            gasto = get_object_or_404(Expense, pk=gasto_id, pedido=pedido, shopper=shopper_profile)
            if monto_raw.isdigit():
                gasto.monto = int(monto_raw)
                gasto.save()
            return redirect("shopper_order_detail", pk=pedido.pk)

        # NUEVO: Borrar un gasto (línea completa)
        if "borrar_gasto_pedido" in request.POST:
            gasto_id = request.POST.get("gasto_id")
            gasto = get_object_or_404(Expense, pk=gasto_id, pedido=pedido, shopper=shopper_profile)
            gasto.delete()
            return redirect("shopper_order_detail", pk=pedido.pk)

        # Aprobar pago reportado por cliente
        if "aprobar_pago" in request.POST:
            pago_id = request.POST.get("pago_id")
            pago = get_object_or_404(Payment, pk=pago_id, pedido=pedido)
            pago.aprobado = True
            pago.save()
            return redirect("shopper_order_detail", pk=pedido.pk)

        # Agregar pago (shopper)
        if "agregar_pago" in request.POST:
            pago_form = PaymentForm(request.POST)
            if pago_form.is_valid():
                pago = pago_form.save(commit=False)
                pago.pedido = pedido
                pago.creado_por = "SHOPPER"
                pago.aprobado = True
                pago.save()
                return redirect("shopper_order_detail", pk=pedido.pk)

        # Agregar gasto (pedido)
        if "agregar_gasto" in request.POST:
            gasto_form = ExpenseProductoForm(request.POST)
            if gasto_form.is_valid():
                gasto = gasto_form.save(commit=False)
                gasto.pedido = pedido
                gasto.shopper = shopper_profile
                gasto.save()
                return redirect("shopper_order_detail", pk=pedido.pk)

    cliente = pedido.customer
    whatsapp_cliente = cliente.whatsapp_link

    pagos_pendientes = pedido.pagos.filter(aprobado=False).order_by("-creado")

    context = {
        "shopper": shopper_profile,
        "pedido": pedido,
        "pago_form": pago_form,
        "gasto_form": gasto_form,
        "whatsapp_cliente": whatsapp_cliente,  # shopper -> cliente
        "pagos_pendientes": pagos_pendientes,
    }
    return render(request, "marketplace/shopper_order_detail.html", context)



@login_required
def shopper_gastos_generales(request):
    shopper_profile = get_object_or_404(ShopperProfile, user=request.user)

    gastos = Expense.objects.filter(
        shopper=shopper_profile, pedido__isnull=True
    ).order_by("-creado")

    # Form de creación (mantiene tu comportamiento actual)
    form = ExpenseGeneralForm()

    if request.method == "POST":
        # EDITAR inline (misma fila)
        if "edit_gasto" in request.POST:
            gasto_id = request.POST.get("gasto_id")
            gasto = get_object_or_404(
                Expense,
                pk=gasto_id,
                shopper=shopper_profile,
                pedido__isnull=True,
            )
            edit_form = ExpenseGeneralForm(request.POST, instance=gasto)
            if edit_form.is_valid():
                g = edit_form.save(commit=False)
                g.shopper = shopper_profile
                g.pedido = None
                g.save()
            return redirect("shopper_gastos_generales")

        # CREAR nuevo gasto general
        form = ExpenseGeneralForm(request.POST)
        if form.is_valid():
            gasto = form.save(commit=False)
            gasto.shopper = shopper_profile
            gasto.pedido = None
            gasto.save()
            return redirect("shopper_gastos_generales")

    return render(
        request,
        "marketplace/shopper_gastos_generales.html",
        {
            "shopper": shopper_profile,
            "gastos": gastos,
            "form": form,
            "currency_choices": CURRENCY_CHOICES,
            "categoria_choices": Expense.CATEGORIA_CHOICES,
        },
    )


@login_required
def customer_dashboard(request):
    customer_profile = get_object_or_404(CustomerProfile, user=request.user)

    pedidos = (
        customer_profile.pedidos.select_related("shopper")
        .prefetch_related("pagos", "gastos", "articulos")
        .order_by("-creado")
    )

    if request.method == "POST":
        order_id = request.POST.get("order_id")
        rating_raw = request.POST.get("rating")
        comment = (request.POST.get("comment") or "").strip()

        try:
            rating = int(rating_raw)
        except (TypeError, ValueError):
            rating = None

        if order_id and rating in [1, 2, 3, 4, 5]:
            pedido = get_object_or_404(
                Order,
                pk=order_id,
                customer=customer_profile,
                estado="ENTREGADO",
            )
            if not Review.objects.filter(order=pedido).exists():
                Review.objects.create(
                    order=pedido,
                    shopper=pedido.shopper,
                    customer=customer_profile,
                    rating=rating,
                    comment=comment,
                )
                if pedido.shopper:
                    agg = Review.objects.filter(shopper=pedido.shopper).aggregate(avg=Avg("rating"))
                    pedido.shopper.calificacion = agg["avg"] or 0
                    pedido.shopper.save()

            return redirect("customer_dashboard")

    pedidos_pendientes_resena = pedidos.filter(
        estado="ENTREGADO",
        review__isnull=True,
    )

    return render(
        request,
        "marketplace/customer_dashboard.html",
        {
            "customer": customer_profile,
            "pedidos": pedidos,
            "pedidos_pendientes_resena": pedidos_pendientes_resena,
        },
    )


@login_required
def order_detail(request, pk):
    customer_profile = get_object_or_404(CustomerProfile, user=request.user)
    pedido = get_object_or_404(Order, pk=pk, customer=customer_profile)

    whatsapp_shopper = None
    if pedido.shopper:
        whatsapp_shopper = pedido.shopper.whatsapp_link

    if request.method == "POST" and "reportar_pago" in request.POST:
        monto_raw = (request.POST.get("monto") or "").strip()
        tipo_pago = request.POST.get("tipo_pago") or "PARCIAL"
        metodo = request.POST.get("metodo") or "OTRO"
        nota = (request.POST.get("nota") or "").strip()

        if monto_raw.isdigit():
            Payment.objects.create(
                pedido=pedido,
                monto=int(monto_raw),
                tipo_pago=tipo_pago,
                metodo=metodo,
                nota=nota,
                creado_por="CLIENTE",
                aprobado=False,
            )
        return redirect("order_detail", pk=pedido.pk)

    return render(
        request,
        "marketplace/order_detail.html",
        {
            "pedido": pedido,
            "whatsapp_shopper": whatsapp_shopper,
        },
    )


@login_required
def create_order(request):
    customer_profile = get_object_or_404(CustomerProfile, user=request.user)

    if request.method == "POST":
        form = OrderForm(request.POST)
        try:
            numero_articulos = int(request.POST.get("numero_articulos", "1") or 1)
        except ValueError:
            numero_articulos = 1

        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.customer = customer_profile

            if pedido.shopper:
                pedido.estado = "EN_SELECCION"
            else:
                pedido.estado = "BUSCANDO_SHOPPER"

            pedido.save()

            nombres = []
            for i in range(1, numero_articulos + 1):
                nombre = (request.POST.get(f"articulo_{i}_nombre") or "").strip()
                if not nombre:
                    continue

                nombres.append(nombre)

                categoria = request.POST.get(f"articulo_{i}_categoria") or "OTRO"
                cantidad_raw = request.POST.get(f"articulo_{i}_cantidad")
                try:
                    cantidad = int(cantidad_raw or 1)
                except ValueError:
                    cantidad = 1
                nota = (request.POST.get(f"articulo_{i}_nota") or "").strip()

                OrderItem.objects.create(
                    pedido=pedido,
                    nombre=nombre,
                    categoria=categoria,
                    cantidad=cantidad,
                    nota=nota,
                )

            if nombres:
                pedido.titulo = " + ".join(nombres[:3]) + ("…" if len(nombres) > 3 else "")
                pedido.save()

            return redirect("customer_dashboard")
    else:
        form = OrderForm()
        numero_articulos = 1

    categorias_articulo = OrderItem.CATEGORIA_ARTICULO_CHOICES
    top_shoppers = get_top_shoppers_for_customer(customer_profile)

    return render(
        request,
        "marketplace/create_order.html",
        {
            "form": form,
            "numero_articulos": numero_articulos,
            "categorias_articulo": categorias_articulo,
            "top_shoppers": top_shoppers,
        },
    )


def logout_view(request):
    logout(request)
    return redirect("home")


def buscar_shoppers(request):
    shoppers = ShopperProfile.objects.filter(
        acepta_nuevos_pedidos=True
    ).order_by("-calificacion", "-creado")

    return render(
        request,
        "marketplace/buscar_shoppers.html",
        {"shoppers": shoppers},
    )


def como_funciona(request):
    return render(request, "marketplace/como_funciona.html")


def faqs(request):
    return render(request, "marketplace/faqs.html")
