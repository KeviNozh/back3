from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import *

# Registrar permisos personalizados en el admin
admin.site.register(Permission)

# Extender el UserAdmin para incluir perfiles
class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil Usuario'

class UsuarioPersonalizadoAdmin(UserAdmin):
    inlines = (PerfilUsuarioInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'tipo_usuario')
    list_filter = ('is_staff', 'is_superuser', 'perfilusuario__tipo_usuario')
    
    def tipo_usuario(self, obj):
        try:
            return obj.perfilusuario.tipo_usuario
        except:
            return "Sin perfil"
    tipo_usuario.short_description = 'Tipo Usuario'

# Re-registrar User admin
admin.site.unregister(User)
admin.site.register(User, UsuarioPersonalizadoAdmin)

@admin.register(Ruta)
class RutaAdmin(admin.ModelAdmin):
    list_display = ['id', 'origen', 'destino', 'tipo_transporte', 'distancia_km']
    list_filter = ['tipo_transporte']
    search_fields = ['origen', 'destino']
    list_per_page = 20
    
    # Permisos de acceso
    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ['id', 'patente', 'tipo_vehiculo', 'modelo', 'capacidad_kg', 'conductor_asignado', 'activo']
    list_filter = ['tipo_vehiculo', 'activo']
    search_fields = ['patente', 'modelo']
    list_per_page = 20
    
    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff

@admin.register(Aeronave)
class AeronaveAdmin(admin.ModelAdmin):
    list_display = ['id', 'matricula', 'tipo_aeronave', 'modelo', 'capacidad_kg', 'piloto_asignado', 'activo']
    list_filter = ['tipo_aeronave', 'activo']
    search_fields = ['matricula', 'modelo']
    list_per_page = 20

@admin.register(Conductor)
class ConductorAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'rut', 'licencia', 'telefono', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'rut', 'licencia']
    list_per_page = 20

@admin.register(Piloto)
class PilotoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'rut', 'certificacion', 'horas_vuelo', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'rut', 'certificacion']
    list_per_page = 20

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['id', 'razon_social', 'rut', 'persona_contacto', 'telefono', 'activo']
    list_filter = ['activo', 'tipo_cliente']
    search_fields = ['razon_social', 'rut', 'persona_contacto']
    list_per_page = 20

@admin.register(Carga)
class CargaAdmin(admin.ModelAdmin):
    list_display = ['id', 'descripcion', 'tipo_carga', 'peso_kg', 'cliente', 'valor_declarado']
    list_filter = ['tipo_carga']
    search_fields = ['descripcion', 'cliente__razon_social']
    list_per_page = 20

@admin.register(Seguro)
class SeguroAdmin(admin.ModelAdmin):
    list_display = ['id', 'numero_poliza', 'tipo_seguro', 'aseguradora', 'cobertura', 'estado', 'vigencia_desde', 'vigencia_hasta']
    list_filter = ['tipo_seguro', 'estado']
    search_fields = ['numero_poliza', 'aseguradora']
    list_per_page = 20

@admin.register(Despacho)
class DespachoAdmin(admin.ModelAdmin):
    list_display = ['id', 'ruta', 'estado', 'costo_envio', 'fecha_despacho', 'cliente']
    list_filter = ['estado', 'fecha_despacho']
    search_fields = ['ruta__origen', 'ruta__destino', 'cliente__razon_social']
    list_per_page = 20

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'tipo_usuario', 'conductor_nombre', 'piloto_nombre', 'telefono', 'fecha_creacion']
    list_filter = ['tipo_usuario']
    search_fields = ['usuario__username', 'usuario__first_name', 'usuario__last_name']
    
    def conductor_nombre(self, obj):
        return obj.conductor_asignado.nombre if obj.conductor_asignado else "-"
    conductor_nombre.short_description = 'Conductor'
    
    def piloto_nombre(self, obj):
        return obj.piloto_asignado.nombre if obj.piloto_asignado else "-"
    piloto_nombre.short_description = 'Piloto'

# Configuración del sitio admin
admin.site.site_header = "Logística Global - Administración"
admin.site.site_title = "Sistema de Logística Global"
admin.site.index_title = "Panel de Administración"  