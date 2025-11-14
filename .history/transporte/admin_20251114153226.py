from django.contrib import admin
from .models import *

@admin.register(Ruta)
class RutaAdmin(admin.ModelAdmin):
    list_display = ['id', 'origen', 'destino', 'tipo_transporte', 'distancia_km']
    list_filter = ['tipo_transporte']
    search_fields = ['origen', 'destino']

@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ['id', 'patente', 'tipo_vehiculo', 'modelo', 'capacidad_kg', 'conductor_asignado', 'activo']
    list_filter = ['tipo_vehiculo', 'activo']
    search_fields = ['patente', 'modelo']

@admin.register(Aeronave)
class AeronaveAdmin(admin.ModelAdmin):
    list_display = ['id', 'matricula', 'tipo_aeronave', 'modelo', 'capacidad_kg', 'piloto_asignado', 'activo']
    list_filter = ['tipo_aeronave', 'activo']
    search_fields = ['matricula', 'modelo']

@admin.register(Conductor)
class ConductorAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'rut', 'licencia', 'telefono', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'rut', 'licencia']

@admin.register(Piloto)
class PilotoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'rut', 'certificacion', 'horas_vuelo', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'rut', 'certificacion']

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['id', 'razon_social', 'rut', 'persona_contacto', 'telefono', 'activo']
    list_filter = ['activo']
    search_fields = ['razon_social', 'rut', 'persona_contacto']

@admin.register(Carga)
class CargaAdmin(admin.ModelAdmin):
    list_display = ['id', 'descripcion', 'tipo_carga', 'peso_kg', 'cliente', 'valor_declarado']
    list_filter = ['tipo_carga']
    search_fields = ['descripcion', 'cliente__razon_social']

@admin.register(Seguro)
class SeguroAdmin(admin.ModelAdmin):
    list_display = ['id', 'numero_poliza', 'tipo_seguro', 'aseguradora', 'cobertura', 'estado', 'vigencia_desde', 'vigencia_hasta']
    list_filter = ['tipo_seguro', 'estado']
    search_fields = ['numero_poliza', 'aseguradora']

@admin.register(Despacho)
class DespachoAdmin(admin.ModelAdmin):
    list_display = ['id', 'ruta', 'estado', 'costo_envio', 'fecha_despacho', 'cliente']
    list_filter = ['estado', 'fecha_despacho']
    search_fields = ['ruta__origen', 'ruta__destino', 'cliente__razon_social']

# Registrar el modelo de perfil de usuario si existe
@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'telefono', 'departamento', 'fecha_creacion']
============================================================


===== apps.py =====
from django.apps import AppConfig


class TransporteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transporte'