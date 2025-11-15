from django.shortcuts import redirect
from django.contrib import messages

class PermisosMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Solo aplicar a usuarios autenticados
        if not request.user.is_authenticated:
            return None

        # URLs públicas para todos los usuarios autenticados
        urls_publicas = ['login', 'logout', 'register', 'dashboard']
        
        if request.resolver_match.url_name in urls_publicas:
            return None

        # Obtener el tipo de usuario
        try:
            # Si es superusuario, dar acceso completo
            if request.user.is_superuser:
                return None
                
            # ✅ MANEJO ROBUSTO DE PERFILES - CORREGIDO
            if hasattr(request.user, 'perfilusuario'):
                tipo_usuario = request.user.perfilusuario.tipo_usuario
            else:
                # Si no tiene perfil, crear uno por defecto
                from .models import PerfilUsuario
                PerfilUsuario.objects.create(
                    usuario=request.user,
                    tipo_usuario='CLIENTE'
                )
                tipo_usuario = 'CLIENTE'
        except Exception as e:
            # En caso de cualquier error, usar CLIENTE como predeterminado
            print(f"Error en middleware de permisos: {e}")
            tipo_usuario = 'CLIENTE'

        # ✅ DEFINIR PERMISOS ACTUALIZADOS - CORREGIDOS
        permisos = {
            'ADMIN': [
                'despachos', 'rutas', 'vehiculos', 'aeronaves', 'conductores', 
                'pilotos', 'clientes', 'cargas', 'seguros', 'reportes', 'api',
                'despacho_crear', 'despacho_editar', 'despacho_eliminar',
                'ruta_create', 'ruta_update', 'ruta_delete', 'ruta_list', 'ruta_detail',
                'vehiculo_editar', 'aeronave_editar', 'conductor_editar',
                'piloto_editar', 'cliente_editar', 'carga_editar', 'seguro_editar',
                'aeronave_eliminar', 'generar_reporte_pdf', 'obtener_datos_reporte',
                'gestion_usuarios', 'editar_usuario', 'asignar_conductor_piloto',
                'vehiculo_crear', 'vehiculo_eliminar', 'aeronave_crear',
                'conductor_crear', 'conductor_eliminar', 'piloto_crear',
                'piloto_eliminar', 'cliente_crear', 'cliente_eliminar',
                'carga_crear', 'carga_eliminar', 'seguro_crear', 'seguro_eliminar'
            ],
            'CLIENTE': [
                # ✅ PERMISOS ACTUALIZADOS PARA VER LAS SECCIONES
                'despachos', 'rutas', 'vehiculos', 'aeronaves', 'conductores', 
                'pilotos', 'clientes', 'cargas', 'seguros', 'api',
                'ruta_list', 'ruta_detail', 'despacho_detail'
            ],
            'CONDUCTOR': [
                'despachos', 'vehiculos', 'rutas', 'cargas', 'ruta_list', 'ruta_detail',
                'despacho_detail', 'conductores', 'clientes', 'api'
            ],
            'PILOTO': [
                'despachos', 'aeronaves', 'rutas', 'cargas', 'ruta_list', 'ruta_detail',
                'despacho_detail', 'pilotos', 'clientes', 'api'
            ]
        }

        url_actual = request.resolver_match.url_name
        
        # Verificar si la URL actual está permitida para este usuario
        if url_actual not in permisos.get(tipo_usuario, []):
            messages.error(request, '❌ No tiene permiso para acceder a esta función')
            return redirect('dashboard')

        return None