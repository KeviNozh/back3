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
                if hasattr(request.user, 'perfilusuario') and request.user.perfilusuario.tipo_usuario != 'ADMIN':
                    messages.error(request, 'Acceso denegado: Solo lectura permitida')
                    return redirect(request.path)
            except:
                messages.error(request, 'Acceso denegado')
                return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view