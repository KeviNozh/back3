# transporte/decorators.py
from django.http import HttpResponseForbidden
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            # ✅ Superusuarios y staff tienen acceso completo
            if request.user.is_superuser or request.user.is_staff:
                return view_func(request, *args, **kwargs)
                
            try:
                if hasattr(request.user, 'perfilusuario') and request.user.perfilusuario.tipo_usuario == 'ADMIN':
                    return view_func(request, *args, **kwargs)
            except:
                pass
        messages.error(request, 'Acceso denegado: Se requiere rol de administrador')
        return redirect('dashboard')
    return _wrapped_view

def solo_lectura(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # ✅ DIAGNÓSTICO MEJORADO
        print(f"🎯 SOLO_LECTURA - URL: {request.resolver_match.url_name}")
        print(f"🎯 SOLO_LECTURA - Método: {request.method}")
        print(f"🎯 SOLO_LECTURA - Usuario: {request.user}")
        print(f"🎯 SOLO_LECTURA - Superuser: {request.user.is_superuser}")
        print(f"🎯 SOLO_LECTURA - Staff: {request.user.is_staff}")
        
        # Si no está autenticado, dejar que Django maneje la redirección
        if not request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        
        # ✅ PERMITIR TODAS LAS ACCIONES A SUPERUSUARIOS, STAFF Y ADMIN
        if request.user.is_superuser or request.user.is_staff:
            print("✅ SOLO_LECTURA: Permitiendo acceso COMPLETO a superuser/staff")
            return view_func(request, *args, **kwargs)
            
        try:
            if hasattr(request.user, 'perfilusuario') and request.user.perfilusuario.tipo_usuario == 'ADMIN':
                print("✅ SOLO_LECTURA: Permitiendo acceso COMPLETO a ADMIN")
                return view_func(request, *args, **kwargs)
        except Exception as e:
            print(f"🎯 SOLO_LECTURA: Error al verificar perfil: {e}")
        
        # ❌ SOLO BLOQUEAR ACCIONES DE ESCRITURA (POST, PUT, DELETE) para usuarios NO-ADMIN
        if request.method in ['POST', 'PUT', 'DELETE']:
            print("🚫 SOLO_LECTURA: Bloqueando acción de escritura para usuario no-admin")
            messages.error(request, 'Acceso denegado: Solo lectura permitida para su tipo de usuario')
            return redirect(request.path)
        
        # ✅ PERMITIR ACCIONES DE LECTURA (GET) a todos los usuarios autenticados
        print("✅ SOLO_LECTURA: Permitiendo acceso de LECTURA")
        return view_func(request, *args, **kwargs)
    return _wrapped_view