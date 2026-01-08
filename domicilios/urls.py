# domicilios/urls.py (Versión final combinada)

# domicilios/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views  # <--- ESTA LÍNEA ES LA QUE FALTA Y CAUSA EL NAMEERROR

# Importamos los ViewSets específicos para el router de la API
from .views import (
    ComercioViewSet, 
    CategoriaViewSet, 
    ProductoViewSet, 
    PedidoViewSet, 
    ItemPedidoViewSet
)

app_name = 'domicilios'

# Configuración del Router
router = DefaultRouter()
router.register(r'comercios', ComercioViewSet, basename='api-comercios')
router.register(r'categorias', CategoriaViewSet, basename='api-categorias')
router.register(r'productos', ProductoViewSet, basename='api-productos')
router.register(r'pedidos', PedidoViewSet, basename='api-pedidos')
router.register(r'items-pedido', ItemPedidoViewSet, basename='api-items')

urlpatterns = [
    # URLs de la Web (Aquí es donde fallaba antes por no tener el import de 'views')
    path('', views.ComercioListView.as_view(), name='comercio_list'),
    path('<int:comercio_id>/productos/', views.ProductoListView.as_view(), name='producto_list'),
    path('carrito/add/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('<int:comercio_id>/checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('pedido/<int:pk>/', views.PedidoDetailView.as_view(), name='pedido_detalle'),
    
    # URLs de Repartidores
    path('repartidor/dashboard/', views.RepartidorDashboardView.as_view(), name='repartidor_dashboard'),
    path('repartidor/recoger/<int:pedido_id>/', views.RecogerPedidoView.as_view(), name='recoger_pedido'),
    path('repartidor/entregar/<int:pedido_id>/', views.EntregarPedidoView.as_view(), name='entregar_pedido'),

    # API para la App Móvil
    path('api/', include(router.urls)),
]