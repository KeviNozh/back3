from django.shortcuts import redirect
from django.contrib import messages

class PermisosMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # ✅ DIAGNÓSTICO
        print("=" * 60)
        print(f"🔍 MIDDLEWARE - URL: {request.resolver_match.url_name}")
        print(f"🔍 MIDDLEWARE - Método: {request.method}")
        print(f"🔍 MIDDLEWARE - Usuario: {request.user}")
        print(f"🔍 MIDDLEWARE - Superuser: {request.user.is_superuser}")
        
        # ✅ PERMITIR ACCESO COMPLETO A SUPERUSUARIOS Y STAFF
        if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
            print("✅ Acceso permitido: Superusuario/Staff")
            return None

        # Solo aplicar a usuarios autenticados
        if not request.user.is_authenticated:
            return None

        # ✅ URLs públicas para todos los usuarios autenticados
        # ✅ AGREGAR ESTAS URLs A LAS URLs PÚBLICAS
        urls_publicas = [
            'login', 'logout', 'register', 'dashboard', 'dashboard_usuario',
            # ✅ AGREGAR TODAS LAS URLs DE CREACIÓN
            'conductor_crear', 'piloto_crear', 'cliente_crear', 'carga_crear', 'seguro_crear',
            'vehiculo_crear', 'aeronave_crear', 'despacho_crear', 'ruta_create',
            'conductor_editar', 'piloto_editar', 'cliente_editar', 'carga_editar', 'seguro_editar',
            'vehiculo_editar', 'aeronave_editar', 'despacho_editar', 'ruta_update'
        ]
        
        if request.resolver_match.url_name in urls_publicas:
            print(f"✅ URL pública: {request.resolver_match.url_name}")
            return None

        # Obtener tipo de usuario
        try:
            if hasattr(request.user, 'perfilusuario'):
                tipo_usuario = request.user.perfilusuario.tipo_usuario
            else:
                from .models import PerfilUsuario
                perfil, created = PerfilUsuario.objects.get_or_create(
                    usuario=request.user,
                    defaults={'tipo_usuario': 'CLIENTE'}
                )
                tipo_usuario = perfil.tipo_usuario
        except Exception as e:
            print(f"Error en middleware: {e}")
            tipo_usuario = 'CLIENTE'

        print(f"🔍 Tipo usuario: {tipo_usuario}")

        # ✅ PERMITIR TODAS LAS ACCIONES A ADMIN
        if tipo_usuario == 'ADMIN':
            print("✅ Acceso permitido: Usuario ADMIN")
            return None

        # Para otros tipos de usuario, usar permisos restrictivos
        permisos = {
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
            
        if url_actual not in permisos.get(tipo_usuario, []):
            print(f"🚫 ACCESO DENEGADO: {tipo_usuario} no puede acceder a {url_actual}")
            messages.error(request, '❌ No tiene permiso para acceder a esta función')
            return redirect('dashboard')

        print(f"✅ ACCESO PERMITIDO: {tipo_usuario} puede acceder a {url_actual}")
        return None
    
def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        print("🔍 ADMIN_REQUIRED - Verificando permisos...")
        print(f"URL: {request.resolver_match.url_name}")
        print(f"Usuario: {request.user}")
        print(f"Superuser: {request.user.is_superuser}")
        print(f"Staff: {request.user.is_staff}")
        
        if request.user.is_authenticated:
            # ✅ PERMITIR a superusuarios, staff y ADMIN
            if request.user.is_superuser or request.user.is_staff:
                print("✅ Acceso permitido: Superuser/Staff")
                return view_func(request, *args, **kwargs)
                
            try:
                if hasattr(request.user, 'perfilusuario') and request.user.perfilusuario.tipo_usuario == 'ADMIN':
                    print("✅ Acceso permitido: ADMIN")
                    return view_func(request, *args, **kwargs)
                else:
                    print(f"❌ Tipo usuario: {request.user.perfilusuario.tipo_usuario}")
            except Exception as e:
                print(f"❌ Error verificando perfil: {e}")
                pass
                
        print("❌ Acceso denegado")
        messages.error(request, 'Acceso denegado: Se requiere rol de administrador')
        return redirect('dashboard')
    return _wrapped_view