# domicilios/urls.py (Versión final combinada)

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
# Importaciones de ViewSets para DRF (Asegúrate de que sean correctas)
from .views import ComercioViewSet, PedidoViewSet, ItemPedidoViewSet 

app_name = 'domicilios'

# --- A. CONFIGURACIÓN DEL ROUTER DRF ---
router = DefaultRouter()

# 🔑 SOLUCIÓN: Definir basename manualmente para evitar AssertionErrors
router.register(r'comercios', ComercioViewSet, basename='comercio_api')
router.register(r'pedidos', PedidoViewSet, basename='pedido_api')
router.register(r'items-pedido', ItemPedidoViewSet, basename='item_pedido_api')


# --- B. RUTAS TRADICIONALES DE DJANGO ---
urlpatterns_tradicional = [
    # URLs de Clientes
    path('', views.ComercioListView.as_view(), name='comercio_list'),
    path('<int:comercio_id>/productos/', views.ProductoListView.as_view(), name='producto_list'),
    path('carrito/add/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('<int:comercio_id>/checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('pedido/<int:pk>/', views.PedidoDetailView.as_view(), name='pedido_detalle'),
    
    # URLs de Repartidores
    path('repartidor/dashboard/', views.RepartidorDashboardView.as_view(), name='repartidor_dashboard'),
    path('repartidor/recoger/<int:pedido_id>/', views.RecogerPedidoView.as_view(), name='recoger_pedido'), # ❌ Tenías .as_as_view()
    path('repartidor/entregar/<int:pedido_id>/', views.EntregarPedidoView.as_view(), name='entregar_pedido'),

    # URLs de Administración
    path('admin/comercios/', views.ComercioListViewAdmin.as_view(), name='admin_comercio_list'),
    path('admin/comercios/crear/', views.ComercioCreateView.as_view(), name='admin_comercio_crear'),
    path('admin/comercios/<int:comercio_id>/productos/', views.ProductoListViewAdmin.as_view(), name='admin_producto_list'),
    path('admin/comercios/<int:comercio_id>/productos/crear/', views.ProductoCreateView.as_view(), name='admin_producto_crear'),
]

# --- C. LISTA FINAL DE URLS ---
# Las rutas de DRF se incluyen bajo el path 'api/' para separarlas si es necesario, 
# pero aquí las combinamos en una sola lista que empieza por las tradicionales.
urlpatterns = urlpatterns_tradicional + [
    # Incluye las rutas de la API DRF (esto crea: /api/v1/domicilios/comercios/, etc.)
    # Si esta app se incluye bajo 'domicilios/' en el urls.py principal,
    # el path vacío ('') es apropiado.
    path('', include(router.urls)), 
]