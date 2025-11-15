from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    RutaListView, RutaDetailView, RutaCreateView, RutaUpdateView, RutaDeleteView,
)
from .decorators import admin_required, solo_lectura  
from .views import (
    api_rutas_list, api_vehiculos_list, api_aeronaves_list, 
    api_conductores_list, api_pilotos_list, api_clientes_list,
    api_cargas_list, api_seguros_list, api_despachos_list
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
    
    # ✅ NUEVAS URLs API ESPECÍFICAS
    path('api/v1/rutas/', api_rutas_list, name='api_rutas_list'),
    path('api/v1/vehiculos/', api_vehiculos_list, name='api_vehiculos_list'),
    path('api/v1/aeronaves/', api_aeronaves_list, name='api_aeronaves_list'),
    path('api/v1/conductores/', api_conductores_list, name='api_conductores_list'),
    path('api/v1/pilotos/', api_pilotos_list, name='api_pilotos_list'),
    path('api/v1/clientes/', api_clientes_list, name='api_clientes_list'),
    path('api/v1/cargas/', api_cargas_list, name='api_cargas_list'),
    path('api/v1/seguros/', api_seguros_list, name='api_seguros_list'),
    path('api/v1/despachos/', api_despachos_list, name='api_despachos_list'),
    
    # Template URLs - Vistas principales
    path('', views.dashboard, name='dashboard'),
    path('despachos/', solo_lectura(views.despachos_view), name='despachos'),
    path('rutas/', solo_lectura(views.rutas_view), name='rutas'),
    path('vehiculos/', solo_lectura(views.vehiculos_view), name='vehiculos'),
    path('aeronaves/', solo_lectura(views.aeronaves_view), name='aeronaves'),
    path('conductores/', solo_lectura(views.conductores_view), name='conductores'),
    path('pilotos/', solo_lectura(views.pilotos_view), name='pilotos'),
    path('clientes/', solo_lectura(views.clientes_view), name='clientes'),
    path('cargas/', solo_lectura(views.cargas_view), name='cargas'),
    path('seguros/', solo_lectura(views.seguros_view), name='seguros'),
    path('reportes/', admin_required(views.reportes_view), name='reportes'),
    path('api-docs/', solo_lectura(views.api_view), name='api'),
    
    # URLs para CRUD de Rutas (solo admin)
    path('rutas/lista/', solo_lectura(RutaListView.as_view()), name='ruta_list'),
    path('rutas/<int:pk>/', solo_lectura(RutaDetailView.as_view()), name='ruta_detail'),
    path('rutas/nueva/', admin_required(RutaCreateView.as_view()), name='ruta_create'),
    path('rutas/<int:pk>/editar/', admin_required(RutaUpdateView.as_view()), name='ruta_update'),
    path('rutas/<int:pk>/eliminar/', admin_required(RutaDeleteView.as_view()), name='ruta_delete'),
    
    # URLs para funcionalidades específicas (solo admin para crear/editar/eliminar)
    path('despachos/crear/', admin_required(views.crear_despacho), name='despacho_crear'),
    path('despachos/<int:pk>/editar/', admin_required(views.editar_despacho), name='despacho_editar'),
    path('despachos/<int:pk>/', solo_lectura(views.despacho_detail), name='despacho_detail'),
    path('despachos/<int:pk>/eliminar/', admin_required(views.eliminar_despacho), name='despacho_eliminar'),
    
    # URLs para gestión de usuarios (solo admin)
    path('usuarios/', admin_required(views.gestion_usuarios), name='gestion_usuarios'),
    path('usuarios/<int:user_id>/editar/', admin_required(views.editar_usuario), name='editar_usuario'),
    path('usuarios/<int:user_id>/asignar/', admin_required(views.asignar_conductor_piloto), name='asignar_conductor_piloto'),
    
    # PDF (solo admin)
    path('reportes/generar-pdf/', admin_required(views.generar_reporte_pdf), name='generar_reporte_pdf'),
    path('api/reportes/datos/', admin_required(views.obtener_datos_reporte), name='obtener_datos_reporte'),
    
    # URLs de edición (solo admin)
    path('vehiculos/<int:pk>/editar/', admin_required(views.editar_vehiculo), name='vehiculo_editar'),
    path('vehiculos/crear/', admin_required(views.crear_vehiculo), name='vehiculo_crear'),
    path('vehiculos/<int:pk>/eliminar/', admin_required(views.eliminar_vehiculo), name='vehiculo_eliminar'),
    
    path('aeronaves/<int:pk>/editar/', admin_required(views.editar_aeronave), name='aeronave_editar'),
    path('aeronaves/crear/', admin_required(views.crear_aeronave), name='aeronave_crear'),
    path('aeronaves/<int:pk>/eliminar/', admin_required(views.eliminar_aeronave), name='aeronave_eliminar'),
    
    path('conductores/<int:pk>/editar/', admin_required(views.editar_conductor), name='conductor_editar'),
    path('conductores/crear/', admin_required(views.crear_conductor), name='conductor_crear'),
    path('conductores/<int:pk>/eliminar/', admin_required(views.eliminar_conductor), name='conductor_eliminar'),
    
    path('pilotos/<int:pk>/editar/', admin_required(views.editar_piloto), name='piloto_editar'),
    path('pilotos/crear/', admin_required(views.crear_piloto), name='piloto_crear'),
    path('pilotos/<int:pk>/eliminar/', admin_required(views.eliminar_piloto), name='piloto_eliminar'),
    
    path('clientes/<int:pk>/editar/', admin_required(views.editar_cliente), name='cliente_editar'),
    path('clientes/crear/', admin_required(views.crear_cliente), name='cliente_crear'),
    path('clientes/<int:pk>/eliminar/', admin_required(views.eliminar_cliente), name='cliente_eliminar'),
    
    path('cargas/<int:pk>/editar/', admin_required(views.editar_carga), name='carga_editar'),
    path('cargas/crear/', admin_required(views.crear_carga), name='carga_crear'),
    path('cargas/<int:pk>/eliminar/', admin_required(views.eliminar_carga), name='carga_eliminar'),
    
    path('seguros/<int:pk>/editar/', admin_required(views.editar_seguro), name='seguro_editar'),
    path('seguros/crear/', admin_required(views.crear_seguro), name='seguro_crear'),
    path('seguros/<int:pk>/eliminar/', admin_required(views.eliminar_seguro), name='seguro_eliminar'),
]