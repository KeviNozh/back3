# transporte/decorators.py
from django.http import HttpResponseForbidden
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
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
        if request.user.is_authenticated and request.method in ['POST', 'PUT', 'DELETE']:
            try:
                # ✅ PERMITIR ACCESO COMPLETO A ADMIN Y SUPERUSUARIOS
                if hasattr(request.user, 'perfilusuario') and request.user.perfilusuario.tipo_usuario == 'ADMIN':
                    return view_func(request, *args, **kwargs)
                if request.user.is_superuser or request.user.is_staff:
                    return view_func(request, *args, **kwargs)
            except:
                pass
            messages.error(request, 'Acceso denegado: Solo lectura permitida')
            return redirect(request.path)
        return view_func(request, *args, **kwargs)
    return _wrapped_view