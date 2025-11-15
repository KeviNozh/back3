# En transporte/decorators.py
from django.http import HttpResponseForbidden
from functools import wraps

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if hasattr(request.user, 'perfilusuario'):
            if request.user.perfilusuario.tipo_usuario == 'ADMIN':
                return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("Acceso denegado: Se requiere rol de administrador")
    return _wrapped_view

def solo_lectura(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if hasattr(request.user, 'perfilusuario'):
            if request.user.perfilusuario.tipo_usuario != 'ADMIN':
                if request.method in ['POST', 'PUT', 'DELETE']:
                    return HttpResponseForbidden("Acceso denegado: Solo lectura permitida")
        return view_func(request, *args, **kwargs)
    return _wrapped_view