# domicilios/views.py
# domicilios/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import CreateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse, Http404

# API Rest Framework
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

# Modelos y Serializadores
from .models import Comercio, Producto, Pedido, ItemPedido, Categoria, Mensaje
from .serializers import (
    ComercioSerializer, PedidoSerializer, 
    ItemPedidoSerializer, ProductoSerializer, CategoriaSerializer
)

# ----------------------------------------------------------------------
# 1. MIXINS DE SEGURIDAD
# ----------------------------------------------------------------------
class ClienteRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.rol == 'cliente'
    def handle_no_permission(self):
        messages.error(self.request, "Solo los clientes pueden acceder.")
        return redirect('home')

# ----------------------------------------------------------------------
# 2. VISTAS PARA EL SITIO WEB (HTML)
# ----------------------------------------------------------------------
class ComercioListView(ListView):
    model = Comercio
    template_name = 'domicilios/comercio_list.html'
    context_object_name = 'comercios'
    def get_queryset(self):
        return Comercio.objects.filter(activo=True)

class ProductoListView(ListView):
    model = Producto
    template_name = 'domicilios/producto_list.html'
    def get_queryset(self):
        return Producto.objects.filter(comercio_id=self.kwargs.get('comercio_id'), disponible=True)

class AddToCartView(View):
    def post(self, request, *args, **kwargs):
        return JsonResponse({'status': 'ok', 'message': 'Producto añadido'})

class CheckoutView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'domicilios/checkout.html')

class PedidoDetailView(DetailView):
    model = Pedido
    template_name = 'domicilios/pedido_detalle.html'

class RepartidorDashboardView(ListView):
    model = Pedido
    template_name = 'domicilios/repartidor_dashboard.html'

class RecogerPedidoView(View):
    def post(self, request, pedido_id):
        return JsonResponse({'status': 'recogido'})

class EntregarPedidoView(View):
    def post(self, request, pedido_id):
        return JsonResponse({'status': 'entregado'})

# Vistas de Admin
class ComercioListViewAdmin(ListView):
    model = Comercio
    template_name = 'domicilios/admin_comercio_list.html'

class ComercioCreateView(CreateView):
    model = Comercio
    fields = '__all__'
    template_name = 'domicilios/comercio_form.html'

class ProductoListViewAdmin(ListView):
    model = Producto
    template_name = 'domicilios/admin_producto_list.html'

class ProductoCreateView(CreateView):
    model = Producto
    fields = '__all__'
    template_name = 'domicilios/producto_form.html'

# ----------------------------------------------------------------------
# 3. VIEWSETS PARA LA API (LO QUE USA NORBE EN LA APP)
# ----------------------------------------------------------------------
class ComercioViewSet(viewsets.ModelViewSet):
    queryset = Comercio.objects.filter(activo=True)
    serializer_class = ComercioSerializer
    permission_classes = [IsAuthenticated]

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated]

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.filter(disponible=True)
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated]

class PedidoViewSet(viewsets.ModelViewSet):
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Pedido.objects.filter(Q(cliente=self.request.user) | Q(repartidor=self.request.user))
    def perform_create(self, serializer):
        serializer.save(cliente=self.request.user)

class ItemPedidoViewSet(viewsets.ModelViewSet):
    queryset = ItemPedido.objects.all()
    serializer_class = ItemPedidoSerializer
    permission_classes = [IsAuthenticated]