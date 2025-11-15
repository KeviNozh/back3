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
        # ✅ DIAGNÓSTICO
        print(f"🔍 SOLO_LECTURA - URL: {request.resolver_match.url_name}")
        print(f"🔍 SOLO_LECTURA - Método: {request.method}")
        print(f"🔍 SOLO_LECTURA - Usuario: {request.user}")
        print(f"🔍 SOLO_LECTURA - Superuser: {request.user.is_superuser}")
        print(f"🔍 SOLO_LECTURA - Staff: {request.user.is_staff}")
        
        if request.user.is_authenticated and request.method in ['POST', 'PUT', 'DELETE']:
            # ✅ PERMITIR ACCESO COMPLETO A SUPERUSUARIOS Y STAFF
            if request.user.is_superuser or request.user.is_staff:
                print("✅ SOLO_LECTURA: Permitiendo acceso a superuser/staff")
                return view_func(request, *args, **kwargs)
                
            try:
                if hasattr(request.user, 'perfilusuario') and request.user.perfilusuario.tipo_usuario == 'ADMIN':
                    print("✅ SOLO_LECTURA: Permitiendo acceso a ADMIN")
                    return view_func(request, *args, **kwargs)
            except Exception as e:
                print(f"🔍 SOLO_LECTURA: Error al verificar perfil: {e}")
            
            # ❌ BLOQUEAR solo a usuarios no-admin
            print("🚫 SOLO_LECTURA: Bloqueando acceso - usuario no es admin")
            messages.error(request, 'Acceso denegado: Solo lectura permitida')
            return redirect(request.path)
        
        print("✅ SOLO_LECTURA: Método GET o usuario no autenticado - Acceso permitido")
        return view_func(request, *args, **kwargs)
    return _wrapped_view