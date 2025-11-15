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

        # ✅ AGREGAR URLs DE CREACIÓN/EDICIÓN/ELIMINACIÓN A URLs PÚBLICAS PARA ADMIN
        urls_publicas = [
            'login', 'logout', 'register', 'dashboard', 'dashboard_usuario',
            # URLs de CRUD que deben permitirse si el usuario es ADMIN
            'despacho_crear', 'despacho_editar', 'despacho_eliminar',
            'ruta_create', 'ruta_update', 'ruta_delete',
            'vehiculo_crear', 'vehiculo_editar', 'vehiculo_eliminar',
            'aeronave_crear', 'aeronave_editar', 'aeronave_eliminar',
            'conductor_crear', 'conductor_editar', 'conductor_eliminar',
            'piloto_crear', 'piloto_editar', 'piloto_eliminar',
            'cliente_crear', 'cliente_editar', 'cliente_eliminar',
            'carga_crear', 'carga_editar', 'carga_eliminar',
            'seguro_crear', 'seguro_editar', 'seguro_eliminar',
            'generar_reporte_pdf', 'obtener_datos_reporte',
            'gestion_usuarios', 'editar_usuario', 'asignar_conductor_piloto'
        ]
        
        # Obtener el tipo de usuario
        try:
            if hasattr(request.user, 'perfilusuario'):
                tipo_usuario = request.user.perfilusuario.tipo_usuario
            elif request.user.is_superuser:
                from .models import PerfilUsuario
                perfil, created = PerfilUsuario.objects.get_or_create(
                    usuario=request.user,
                    defaults={'tipo_usuario': 'ADMIN'}
                )
                tipo_usuario = 'ADMIN'
            else:
                from .models import PerfilUsuario
                perfil, created = PerfilUsuario.objects.get_or_create(
                    usuario=request.user,
                    defaults={'tipo_usuario': 'CLIENTE'}
                )
                tipo_usuario = perfil.tipo_usuario
        except Exception as e:
            print(f"Error en middleware de permisos: {e}")
            tipo_usuario = 'CLIENTE'

        # ✅ SI ES ADMIN, PERMITIR ACCESO A TODAS LAS URLs PÚBLICAS DEFINIDAS
        if tipo_usuario == 'ADMIN' and request.resolver_match.url_name in urls_publicas:
            return None

        # Para otros tipos de usuario, usar el sistema de permisos existente
        permisos = {
            'ADMIN': urls_publicas,  # Admin tiene acceso a todas las URLs públicas
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
        
        if not url_actual:
            return None
            
        # Verificar si la URL actual está permitida para este usuario
        if url_actual not in permisos.get(tipo_usuario, []):
            messages.error(request, '❌ No tiene permiso para acceder a esta función')
            return redirect('dashboard')

        return None