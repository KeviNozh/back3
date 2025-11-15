from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    RutaListView, RutaDetailView, RutaCreateView, RutaUpdateView, RutaDeleteView,
)

router = DefaultRouter()
router.register(r'rutas', views.RutaViewSet)
router.register(r'vehiculos', views.VehiculoViewSet)
router.register(r'aeronaves', views.AeronaveViewSet)
router.register(r'conductores', views.ConductorViewSet)
router.register(r'pilotos', views.PilotoViewSet)
router.register(r'clientes', views.ClienteViewSet)
router.register(r'cargas', views.CargaViewSet)
router.register(r'seguros', views.SeguroViewSet)
router.register(r'despachos', views.DespachoViewSet)

urlpatterns = [
    # URLs de autenticación
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # API URLs
    path('api/', include(router.urls)),
    
    # Template URLs - Vistas principales
    path('', views.dashboard, name='dashboard'),
    path('despachos/', views.despachos_view, name='despachos'),
    path('rutas/', views.rutas_view, name='rutas'),
    path('vehiculos/', views.vehiculos_view, name='vehiculos'),
    path('aeronaves/', views.aeronaves_view, name='aeronaves'),
    path('conductores/', views.conductores_view, name='conductores'),
    path('pilotos/', views.pilotos_view, name='pilotos'),
    path('clientes/', views.clientes_view, name='clientes'),
    path('cargas/', views.cargas_view, name='cargas'),
    path('seguros/', views.seguros_view, name='seguros'),
    path('reportes/', views.reportes_view, name='reportes'),
    path('api-docs/', views.api_view, name='api'),  # COMENTADA O ELIMINADA
    
    # URLs para CRUD de Rutas (ejemplo)
    path('rutas/lista/', RutaListView.as_view(), name='ruta_list'),
    path('rutas/<int:pk>/', RutaDetailView.as_view(), name='ruta_detail'),
    path('rutas/nueva/', RutaCreateView.as_view(), name='ruta_create'),
    path('rutas/<int:pk>/editar/', RutaUpdateView.as_view(), name='ruta_update'),
    path('rutas/<int:pk>/eliminar/', RutaDeleteView.as_view(), name='ruta_delete'),
    
    # URLs para funcionalidades específicas
    path('despachos/crear/', views.crear_despacho, name='despacho_crear'),
    path('despachos/<int:pk>/editar/', views.editar_despacho, name='despacho_editar'),
    path('despachos/<int:pk>/', views.despacho_detail, name='despacho_detail'),
    path('despachos/<int:pk>/eliminar/', views.eliminar_despacho, name='despacho_eliminar'),
    
    # PDF
    path('reportes/generar-pdf/', views.generar_reporte_pdf, name='generar_reporte_pdf'),
    path('api/reportes/datos/', views.obtener_datos_reporte, name='obtener_datos_reporte'),
    
    path('vehiculos/<int:pk>/editar/', views.editar_vehiculo, name='vehiculo_editar'),
    path('aeronaves/<int:pk>/editar/', views.editar_aeronave, name='aeronave_editar'),
    path('vehiculos/', solo_lectura(vehiculos_view), name='vehiculos'),
    path('aeronaves/', solo_lectura(aeronaves_view), name='aeronaves'),
    path('conductores/<int:pk>/editar/', views.editar_conductor, name='conductor_editar'),
    path('pilotos/<int:pk>/editar/', views.editar_piloto, name='piloto_editar'),
    path('clientes/<int:pk>/editar/', views.editar_cliente, name='cliente_editar'),
    path('cargas/<int:pk>/editar/', views.editar_carga, name='carga_editar'),
    path('seguros/<int:pk>/editar/', views.editar_seguro, name='seguro_editar'),
    
    path('aeronaves/<int:pk>/eliminar/', views.eliminar_aeronave, name='aeronave_eliminar'),
]