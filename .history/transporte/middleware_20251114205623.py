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
            if hasattr(request.user, 'perfilusuario'):
                tipo_usuario = request.user.perfilusuario.tipo_usuario
            else:
                # Si no tiene perfil, redirigir al dashboard
                messages.error(request, 'Complete su perfil de usuario')
                return redirect('dashboard')
        except Exception as e:
            tipo_usuario = 'CLIENTE'

        # Definir permisos por rol
        permisos = {
            'ADMIN': [
                'despachos', 'rutas', 'vehiculos', 'aeronaves', 'conductores', 
                'pilotos', 'clientes', 'cargas', 'seguros', 'reportes', 'api',
                'despacho_crear', 'despacho_editar', 'despacho_eliminar',
                'ruta_create', 'ruta_update', 'ruta_delete', 'ruta_list', 'ruta_detail',
                'vehiculo_editar', 'aeronave_editar', 'conductor_editar',
                'piloto_editar', 'cliente_editar', 'carga_editar', 'seguro_editar',
                'aeronave_eliminar', 'generar_reporte_pdf', 'obtener_datos_reporte'
            ],
            'CLIENTE': [
                'vehiculos', 'rutas', 'aeronaves', 'ruta_list', 'ruta_detail'
            ],
            'CONDUCTOR': [
                'despachos', 'vehiculos', 'rutas', 'cargas', 'ruta_list', 'ruta_detail',
                'despacho_detail'
            ],
            'PILOTO': [
                'despachos', 'aeronaves', 'rutas', 'cargas', 'ruta_list', 'ruta_detail',
                'despacho_detail'
            ]
        }

        url_actual = request.resolver_match.url_name
        
        # Verificar si la URL actual está permitida para este usuario
        if url_actual not in permisos.get(tipo_usuario, []):
            messages.error(request, 'No tienes permisos para acceder a esta sección')
            return redirect('dashboard')

        return None