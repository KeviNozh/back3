# En transporte/middleware.py
from django.shortcuts import redirect
from django.contrib import messages

class PermisosMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.user.is_authenticated:
            return None

        # URLs permitidas para todos los usuarios autenticados
        urls_publicas = ['login', 'logout', 'dashboard']
        
        if request.resolver_match.url_name in urls_publicas:
            return None

        # Obtener el tipo de usuario
        try:
            perfil = request.user.perfilusuario
            tipo_usuario = perfil.tipo_usuario
        except:
            tipo_usuario = 'CLIENTE'  # Default

        # Definir permisos por rol
        permisos = {
            'ADMIN': [
                'despachos', 'rutas', 'vehiculos', 'aeronaves', 'conductores', 
                'pilotos', 'clientes', 'cargas', 'seguros', 'reportes', 'api',
                'despacho_crear', 'despacho_editar', 'despacho_eliminar',
                'ruta_create', 'ruta_update', 'ruta_delete',
                'vehiculo_editar', 'aeronave_editar', 'conductor_editar',
                'piloto_editar', 'cliente_editar', 'carga_editar', 'seguro_editar'
            ],
            'CLIENTE': [
                'vehiculos', 'rutas', 'aeronaves'  # Solo lectura
            ],
            'CONDUCTOR': [
                'despachos', 'vehiculos', 'rutas', 'cargas'  # Solo lectura
            ],
            'PILOTO': [
                'despachos', 'aeronaves', 'rutas', 'cargas'  # Solo lectura
            ]
        }

        url_actual = request.resolver_match.url_name
        
        # Verificar si la URL actual está permitida para este usuario
        if url_actual not in permisos.get(tipo_usuario, []):
            messages.error(request, 'No tienes permisos para acceder a esta sección')
            return redirect('dashboard')

        return None