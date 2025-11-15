from django.shortcuts import redirect
from django.contrib import messages

class PermisosMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

     def process_view(self, request, view_func, view_args, view_kwargs):
        # ✅ PERMITIR ACCESO COMPLETO A SUPERUSUARIOS Y STAFF
        if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
            return None

        # Solo aplicar a usuarios autenticados
        if not request.user.is_authenticated:
            return None

        # URLs públicas para todos los usuarios autenticados
        urls_publicas = ['login', 'logout', 'register', 'dashboard', 'dashboard_usuario']
        
        if request.resolver_match.url_name in urls_publicas:
            return None

        # Obtener el tipo de usuario - MEJORADO
        try:
            if hasattr(request.user, 'perfilusuario'):
                tipo_usuario = request.user.perfilusuario.tipo_usuario
            elif request.user.is_superuser:
                # Si es superusuario y no tiene perfil, crear uno automáticamente
                from .models import PerfilUsuario
                perfil, created = PerfilUsuario.objects.get_or_create(
                    usuario=request.user,
                    defaults={'tipo_usuario': 'ADMIN'}
                )
                tipo_usuario = 'ADMIN'
            else:
                # Si no tiene perfil y no es superusuario, crear uno por defecto
                from .models import PerfilUsuario
                perfil, created = PerfilUsuario.objects.get_or_create(
                    usuario=request.user,
                    defaults={'tipo_usuario': 'CLIENTE'}
                )
                tipo_usuario = perfil.tipo_usuario
        except Exception as e:
            print(f"Error en middleware de permisos: {e}")
            tipo_usuario = 'CLIENTE'

        # ✅ DEFINIR PERMISOS COMPLETOS Y ACTUALIZADOS
        permisos = {
            'ADMIN': [
                # URLs de visualización
                'despachos', 'rutas', 'vehiculos', 'aeronaves', 'conductores', 
                'pilotos', 'clientes', 'cargas', 'seguros', 'reportes', 'api',
                
                # URLs de CRUD para despachos
                'despacho_crear', 'despacho_editar', 'despacho_eliminar', 'despacho_detail',
                
                # URLs de CRUD para rutas
                'ruta_create', 'ruta_update', 'ruta_delete', 'ruta_list', 'ruta_detail',
                
                # URLs de CRUD para vehículos
                'vehiculo_crear', 'vehiculo_editar', 'vehiculo_eliminar', 'vehiculo_detail',
                
                # URLs de CRUD para aeronaves
                'aeronave_crear', 'aeronave_editar', 'aeronave_eliminar', 'aeronave_detail',
                
                # URLs de CRUD para conductores
                'conductor_crear', 'conductor_editar', 'conductor_eliminar', 'conductor_detail',
                
                # URLs de CRUD para pilotos
                'piloto_crear', 'piloto_editar', 'piloto_eliminar', 'piloto_detail',
                
                # URLs de CRUD para clientes
                'cliente_crear', 'cliente_editar', 'cliente_eliminar', 'cliente_detail',
                
                # URLs de CRUD para cargas
                'carga_crear', 'carga_editar', 'carga_eliminar', 'carga_detail',
                
                # URLs de CRUD para seguros
                'seguro_crear', 'seguro_editar', 'seguro_eliminar', 'seguro_detail',
                
                # URLs de reportes y gestión
                'generar_reporte_pdf', 'obtener_datos_reporte',
                'gestion_usuarios', 'editar_usuario', 'asignar_conductor_piloto',
            ],
            'CLIENTE': [
                'despachos', 'rutas', 'vehiculos', 'aeronaves', 'conductores', 
                'pilotos', 'clientes', 'cargas', 'seguros', 'api',
                'ruta_list', 'ruta_detail', 'despacho_detail',
                'vehiculo_detail', 'aeronave_detail', 'conductor_detail',
                'piloto_detail', 'cliente_detail', 'carga_detail', 'seguro_detail'
            ],
            'CONDUCTOR': [
                'despachos', 'vehiculos', 'rutas', 'cargas', 'ruta_list', 'ruta_detail',
                'despacho_detail', 'conductores', 'clientes', 'api',
                'vehiculo_detail', 'aeronave_detail', 'conductor_detail',
                'piloto_detail', 'cliente_detail', 'carga_detail', 'seguro_detail'
            ],
            'PILOTO': [
                'despachos', 'aeronaves', 'rutas', 'cargas', 'ruta_list', 'ruta_detail',
                'despacho_detail', 'pilotos', 'clientes', 'api',
                'vehiculo_detail', 'aeronave_detail', 'conductor_detail',
                'piloto_detail', 'cliente_detail', 'carga_detail', 'seguro_detail'
            ]
        }

        url_actual = request.resolver_match.url_name
        
        # Si no hay URL name, permitir acceso (puede ser una URL que no está en urlpatterns)
        if not url_actual:
            return None
            
        # Verificar si la URL actual está permitida para este usuario
        if url_actual not in permisos.get(tipo_usuario, []):
            messages.error(request, '❌ No tiene permiso para acceder a esta función')
            return redirect('dashboard')

        return None