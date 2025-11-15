from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import viewsets, permissions
from .models import *
from .serializers import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse, JsonResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from datetime import datetime
import io
import json
from .decorators import admin_required, solo_lectura
from functools import wraps
from rest_framework.decorators import api_view as drf_api_view, permission_classes
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views import View
# @method_decorator(login_required, name='dispatch')
# class ApiView(View):
#     def get(self, request):
#        return render(request, 'transporte/api.html')

class AdminOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado que permite:
    - Lectura pública para todos
    - Escritura solo para administradores
    """
    def has_permission(self, request, view):
        # Permitir todas las solicitudes GET, HEAD, OPTIONS (lectura)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Para escritura (POST, PUT, DELETE), verificar si es admin
        return request.user and (
            request.user.is_superuser or 
            request.user.is_staff or
            (hasattr(request.user, 'perfilusuario') and 
             request.user.perfilusuario.tipo_usuario == 'ADMIN')
        )

# Vistas para API - ACTUALIZAR CON PERMISOS
class RutaViewSet(viewsets.ModelViewSet):
    queryset = Ruta.objects.all()
    serializer_class = RutaSerializer
    permission_classes = [AdminOrReadOnly]  # ✅ Cambiado

class VehiculoViewSet(viewsets.ModelViewSet):
    queryset = Vehiculo.objects.all()
    serializer_class = VehiculoSerializer
    permission_classes = [AdminOrReadOnly]  # ✅ Cambiado

class AeronaveViewSet(viewsets.ModelViewSet):
    queryset = Aeronave.objects.all()
    serializer_class = AeronaveSerializer
    permission_classes = [AdminOrReadOnly]  # ✅ Cambiado

class ConductorViewSet(viewsets.ModelViewSet):
    queryset = Conductor.objects.all()
    serializer_class = ConductorSerializer
    permission_classes = [AdminOrReadOnly]  # ✅ Cambiado

class PilotoViewSet(viewsets.ModelViewSet):
    queryset = Piloto.objects.all()
    serializer_class = PilotoSerializer
    permission_classes = [AdminOrReadOnly]  # ✅ Cambiado

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [AdminOrReadOnly]  # ✅ Cambiado

class CargaViewSet(viewsets.ModelViewSet):
    queryset = Carga.objects.all()
    serializer_class = CargaSerializer
    permission_classes = [AdminOrReadOnly]  # ✅ Cambiado

class SeguroViewSet(viewsets.ModelViewSet):
    queryset = Seguro.objects.all()
    serializer_class = SeguroSerializer
    permission_classes = [AdminOrReadOnly]  # ✅ Cambiado

class DespachoViewSet(viewsets.ModelViewSet):
    queryset = Despacho.objects.all()
    serializer_class = DespachoSerializer
    permission_classes = [AdminOrReadOnly]  # ✅ Cambiado
# Vistas basadas en clases para templates HTML
class RutaListView(LoginRequiredMixin, ListView):
    model = Ruta
    template_name = 'transporte/rutas.html'
    context_object_name = 'rutas'

class RutaDetailView(LoginRequiredMixin, DetailView):
    model = Ruta
    template_name = 'transporte/ruta_detail.html'

class RutaCreateView(LoginRequiredMixin, CreateView):
    model = Ruta
    template_name = 'transporte/ruta_form.html'
    fields = ['origen', 'destino', 'tipo_transporte', 'distancia_km']
    success_url = reverse_lazy('rutas')

class RutaUpdateView(LoginRequiredMixin, UpdateView):
    model = Ruta
    template_name = 'transporte/ruta_form.html'
    fields = ['origen', 'destino', 'tipo_transporte', 'distancia_km']
    success_url = reverse_lazy('rutas')

class RutaDeleteView(LoginRequiredMixin, DeleteView):
    model = Ruta
    template_name = 'transporte/ruta_confirm_delete.html'
    success_url = reverse_lazy('rutas')

@login_required
def generar_reporte_pdf(request):
    """Genera un reporte en PDF con datos reales de la base de datos"""
    
    # Crear el buffer para el PDF
    buffer = io.BytesIO()
    
    # Crear el documento PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Obtener estilos
    styles = getSampleStyleSheet()
    
    # Estilo personalizado para el título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        textColor=colors.HexColor('#6366f1'),
        alignment=1  # Centrado
    )
    
    # Información del usuario que genera el reporte
    usuario = request.user
    fecha_generacion = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    # Título del reporte
    elements.append(Paragraph("REPORTE DE LOGÍSTICA GLOBAL", title_style))
    elements.append(Spacer(1, 20))
    
    # Información del generador
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.gray
    )
    
    elements.append(Paragraph(f"<b>Generado por:</b> {usuario.get_full_name() or usuario.username}", info_style))
    elements.append(Paragraph(f"<b>Fecha de generación:</b> {fecha_generacion}", info_style))
    elements.append(Spacer(1, 30))
    
    # OBTENER DATOS REALES DE LA BASE DE DATOS
    
    # 1. Estadísticas generales
    total_despachos = Despacho.objects.count()
    despachos_pendientes = Despacho.objects.filter(estado='PENDIENTE').count()
    despachos_en_ruta = Despacho.objects.filter(estado='EN_RUTA').count()
    despachos_entregados = Despacho.objects.filter(estado='ENTREGADO').count()
    
    total_vehiculos = Vehiculo.objects.filter(activo=True).count()
    total_aeronaves = Aeronave.objects.filter(activo=True).count()
    total_clientes = Cliente.objects.filter(activo=True).count()
    
    # 2. Últimos despachos
    ultimos_despachos = Despacho.objects.all().order_by('-fecha_despacho')[:10]
    
    # 3. Cargas por tipo
    cargas_por_tipo = Carga.objects.values('tipo_carga').annotate(total=Count('id'))
    
    # SECCIÓN 1: ESTADÍSTICAS GENERALES
    elements.append(Paragraph("ESTADÍSTICAS GENERALES", styles['Heading2']))
    elements.append(Spacer(1, 15))
    
    # Tabla de estadísticas
    stats_data = [
        ['MÉTRICA', 'VALOR'],
        ['Total Despachos', str(total_despachos)],
        ['Despachos Pendientes', str(despachos_pendientes)],
        ['Despachos en Ruta', str(despachos_en_ruta)],
        ['Despachos Entregados', str(despachos_entregados)],
        ['Vehículos Activos', str(total_vehiculos)],
        ['Aeronaves Activas', str(total_aeronaves)],
        ['Clientes Activos', str(total_clientes)]
    ]
    
    stats_table = Table(stats_data, colWidths=[250, 100])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 1, colors.gray)
    ]))
    
    elements.append(stats_table)
    elements.append(Spacer(1, 30))
    
    # SECCIÓN 2: ÚLTIMOS DESPACHOS
    elements.append(Paragraph("ÚLTIMOS DESPACHOS", styles['Heading2']))
    elements.append(Spacer(1, 15))
    
    if ultimos_despachos:
        despachos_data = [['ID', 'Cliente', 'Ruta', 'Estado', 'Fecha']]
        
        for despacho in ultimos_despachos:
            despachos_data.append([
                str(despacho.id),
                despacho.cliente.razon_social[:20] + '...' if len(despacho.cliente.razon_social) > 20 else despacho.cliente.razon_social,
                f"{despacho.ruta.origen} - {despacho.ruta.destino}",
                despacho.estado,
                despacho.fecha_despacho.strftime("%d/%m/%Y")
            ])
        
        despachos_table = Table(despachos_data, colWidths=[50, 120, 150, 80, 80])
        despachos_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#06b6d4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 1, colors.gray),
            ('FONTSIZE', (0, 1), (-1, -1), 8)
        ]))
        
        elements.append(despachos_table)
    else:
        elements.append(Paragraph("No hay despachos registrados.", styles['Normal']))
    
    elements.append(Spacer(1, 30))
    
    # SECCIÓN 3: CARGAS POR TIPO
    elements.append(Paragraph("DISTRIBUCIÓN DE CARGAS POR TIPO", styles['Heading2']))
    elements.append(Spacer(1, 15))
    
    if cargas_por_tipo:
        cargas_data = [['Tipo de Carga', 'Cantidad']]
        
        for carga_tipo in cargas_por_tipo:
            cargas_data.append([
                carga_tipo['tipo_carga'],
                str(carga_tipo['total'])
            ])
        
        cargas_table = Table(cargas_data, colWidths=[300, 100])
        cargas_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 1, colors.gray)
        ]))
        
        elements.append(cargas_table)
    else:
        elements.append(Paragraph("No hay cargas registradas.", styles['Normal']))
    
    # Pie de página
    elements.append(Spacer(1, 50))
    elements.append(Paragraph(
        f"<i>Reporte generado automáticamente por el Sistema de Gestión de Transporte - {fecha_generacion}</i>", 
        info_style
    ))
    
    # Construir el PDF
    doc.build(elements)
    
    # Obtener el valor del buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    # Crear la respuesta HTTP
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_logistica.pdf"'
    response.write(pdf)
    
    return response

# Vistas de autenticación
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'transporte/login.html')

@login_required
def obtener_datos_reporte(request):
    """Vista para obtener datos reales de la base de datos para reportes"""
    report_type = request.GET.get('type', 'despachos')
    
    try:
        if report_type == 'despachos':
            # Datos reales de despachos
            despachos = Despacho.objects.select_related('cliente', 'ruta').all().order_by('-fecha_despacho')[:50]
            data = []
            for despacho in despachos:
                data.append({
                    'id': f"DESP-{despacho.id}",
                    'cliente': despacho.cliente.razon_social,
                    'fecha': despacho.fecha_despacho.strftime("%Y-%m-%d"),
                    'estado': despacho.estado,
                    'valor': float(despacho.costo_envio) if despacho.costo_envio else 0,
                    'destino': f"{despacho.ruta.origen} - {despacho.ruta.destino}",
                    'tipo_transporte': despacho.ruta.tipo_transporte
                })
                
        elif report_type == 'financiero':
            # Datos financieros reales
            ingresos = Despacho.objects.aggregate(total=Sum('costo_envio'))['total'] or 0
            total_despachos = Despacho.objects.count()
            promedio_ingresos = ingresos / total_despachos if total_despachos > 0 else 0
            
            data = [
                {'concepto': 'Ingresos por despachos', 'monto': float(ingresos), 'tipo': 'Ingreso'},
                {'concepto': 'Total despachos realizados', 'monto': total_despachos, 'tipo': 'Metrica'},
                {'concepto': 'Ingreso promedio por despacho', 'monto': float(promedio_ingresos), 'tipo': 'Metrica'},
            ]
            
        elif report_type == 'flota':
            # Datos reales de flota
            vehiculos = Vehiculo.objects.filter(activo=True)
            aeronaves = Aeronave.objects.filter(activo=True)
            data = []
            
            for vehiculo in vehiculos:
                data.append({
                    'id': f"VH-{vehiculo.id}",
                    'tipo': 'Vehículo',
                    'modelo': vehiculo.modelo,
                    'estado': 'Activo' if vehiculo.activo else 'Inactivo',
                    'mantenimiento': 'Al día',  # Puedes agregar campo de mantenimiento al modelo
                    'ubicacion': 'Depósito Central',
                    'capacidad': f"{vehiculo.capacidad_kg} kg"
                })
                
            for aeronave in aeronaves:
                data.append({
                    'id': f"AV-{aeronave.id}",
                    'tipo': 'Aeronave',
                    'modelo': aeronave.modelo,
                    'estado': 'Activo' if aeronave.activo else 'Inactivo',
                    'mantenimiento': 'Al día',
                    'ubicacion': 'Aeropuerto',
                    'capacidad': f"{aeronave.capacidad_kg} kg"
                })
                
        elif report_type == 'clientes':
            # Datos reales de clientes
            clientes = Cliente.objects.filter(activo=True)
            data = []
            for cliente in clientes:
                total_despachos = Despacho.objects.filter(cliente=cliente).count()  
                data.append({
                    'id': f"CLI-{cliente.id}",
                    'nombre': cliente.razon_social,
                    'contacto': cliente.persona_contacto,
                    'telefono': cliente.telefono,
                    'email': cliente.email,
                    'volumen': total_despachos,
                    'direccion': cliente.direccion[:50] + '...' if len(cliente.direccion) > 50 else cliente.direccion
                })
                
        elif report_type == 'seguros':
            # Datos reales de seguros
            seguros = Seguro.objects.all()
            data = []
            for seguro in seguros:
                data.append({
                    'poliza': seguro.numero_poliza,
                    'tipo': seguro.tipo_seguro,
                    'aseguradora': seguro.aseguradora,
                    'vencimiento': seguro.vigencia_hasta.strftime("%Y-%m-%d"),
                    'cobertura': float(seguro.cobertura) if seguro.cobertura else 0,
                    'estado': seguro.estado
                })
                
        elif report_type == 'personal':
            # Datos reales de personal
            conductores = Conductor.objects.filter(activo=True)
            pilotos = Piloto.objects.filter(activo=True)
            data = []
            
            for conductor in conductores:
                data.append({
                    'id': f"EMP-C-{conductor.id}",
                    'nombre': conductor.nombre,
                    'puesto': 'Conductor',
                    'estado': 'Activo' if conductor.activo else 'Inactivo',
                    'certificaciones': conductor.licencia,
                    'contacto': conductor.telefono
                })
                
            for piloto in pilotos:
                data.append({
                    'id': f"EMP-P-{piloto.id}",
                    'nombre': piloto.nombre,
                    'puesto': 'Piloto',
                    'estado': 'Activo' if piloto.activo else 'Inactivo',
                    'certificaciones': f"{piloto.certificacion} - {piloto.horas_vuelo} horas",
                    'contacto': piloto.telefono
                })
        
        else:
            data = []
            
        return JsonResponse({'success': True, 'data': data})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        tipo_usuario = request.POST.get('tipo_usuario', 'CLIENTE')  # Nuevo campo
        
        # Validaciones
        if password1 != password2:
            messages.error(request, 'Las contraseñas no coinciden')
            return render(request, 'transporte/login.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya existe')
            return render(request, 'transporte/login.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'El email ya está registrado')
            return render(request, 'transporte/login.html')
        
        # Crear usuario
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )
            user.save()
            
            # ✅ CREAR PERFIL AUTOMÁTICAMENTE
            from .models import PerfilUsuario
            PerfilUsuario.objects.create(
                usuario=user,
                tipo_usuario=tipo_usuario,
                telefono=request.POST.get('telefono', ''),
                departamento=request.POST.get('departamento', '')
            )
            
            # Autenticar y loguear al usuario
            user = authenticate(username=username, password=password1)
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Cuenta creada exitosamente! Bienvenido {user.first_name}')
                return redirect('dashboard')
                
        except Exception as e:
            messages.error(request, f'Error al crear la cuenta: {str(e)}')
    
    return render(request, 'transporte/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente')
    return redirect('login')

@login_required
@admin_required
def gestion_usuarios(request):
    """Vista para gestionar usuarios y sus roles"""
    usuarios = User.objects.all().order_by('-date_joined')
    
    # Filtrar por búsqueda
    search_query = request.GET.get('search', '')
    if search_query:
        usuarios = usuarios.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Obtener perfiles para cada usuario
    usuarios_con_perfiles = []
    for usuario in usuarios:
        try:
            perfil = usuario.perfilusuario
        except:
            # Si no tiene perfil, crear uno por defecto
            perfil = PerfilUsuario.objects.create(
                usuario=usuario,
                tipo_usuario='CLIENTE'
            )
        
        usuarios_con_perfiles.append({
            'usuario': usuario,
            'perfil': perfil
        })
    
    context = {
        'usuarios_con_perfiles': usuarios_con_perfiles,
        'search_query': search_query,
        'tipos_usuario': TipoUsuario.choices,
    }
    return render(request, 'transporte/gestion_usuarios.html', context)

@login_required
@admin_required
def editar_usuario(request, user_id):
    """Vista para editar un usuario"""
    usuario = get_object_or_404(User, id=user_id)
    
    try:
        perfil = usuario.perfilusuario
    except:
        perfil = PerfilUsuario.objects.create(usuario=usuario, tipo_usuario='CLIENTE')
    
    if request.method == 'POST':
        try:
            # Actualizar perfil
            perfil.tipo_usuario = request.POST.get('tipo_usuario')
            perfil.telefono = request.POST.get('telefono', '')
            perfil.departamento = request.POST.get('departamento', '')
            perfil.save()
            
            # Actualizar usuario
            usuario.first_name = request.POST.get('first_name', '')
            usuario.last_name = request.POST.get('last_name', '')
            usuario.email = request.POST.get('email', '')
            usuario.is_active = 'is_active' in request.POST
            usuario.save()
            
            messages.success(request, 'Usuario actualizado exitosamente')
            return redirect('gestion_usuarios')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar el usuario: {str(e)}')
    
    # Obtener conductores y pilotos para asignación
    conductores = Conductor.objects.filter(activo=True)
    pilotos = Piloto.objects.filter(activo=True)
    
    context = {
        'usuario_editar': usuario,
        'perfil': perfil,
        'conductores': conductores,
        'pilotos': pilotos,
        'tipos_usuario': TipoUsuario.choices,
    }
    return render(request, 'transporte/editar_usuario.html', context)

@login_required
@admin_required
def asignar_conductor_piloto(request, user_id):
    """Vista para asignar conductor/piloto a un usuario"""
    usuario = get_object_or_404(User, id=user_id)
    
    try:
        perfil = usuario.perfilusuario
    except:
        perfil = PerfilUsuario.objects.create(usuario=usuario, tipo_usuario='CLIENTE')
    
    if request.method == 'POST':
        try:
            conductor_id = request.POST.get('conductor_asignado')
            piloto_id = request.POST.get('piloto_asignado')
            
            if conductor_id:
                perfil.conductor_asignado_id = conductor_id
            else:
                perfil.conductor_asignado = None
                
            if piloto_id:
                perfil.piloto_asignado_id = piloto_id
            else:
                perfil.piloto_asignado = None
                
            perfil.save()
            messages.success(request, 'Asignaciones actualizadas exitosamente')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar asignaciones: {str(e)}')
    
    return redirect('editar_usuario', user_id=user_id)

# Vistas para templates HTML (funciones)
@login_required
def dashboard(request):
    try:
        tipo_usuario = request.user.perfilusuario.tipo_usuario
    except:
        tipo_usuario = 'CLIENTE'

    # Si es ADMIN o SUPERUSUARIO, mostrar dashboard completo
    if tipo_usuario == 'ADMIN' or request.user.is_superuser:
        # Estadísticas reales para el dashboard ADMIN
        total_despachos = Despacho.objects.count()
        despachos_pendientes = Despacho.objects.filter(estado='PENDIENTE').count()
        despachos_en_ruta = Despacho.objects.filter(estado='EN_RUTA').count()
        despachos_entregados = Despacho.objects.filter(estado='ENTREGADO').count()
        total_vehiculos = Vehiculo.objects.filter(activo=True).count()
        total_aeronaves = Aeronave.objects.filter(activo=True).count()
        total_clientes = Cliente.objects.filter(activo=True).count()
        total_conductores = Conductor.objects.filter(activo=True).count()
        total_pilotos = Piloto.objects.filter(activo=True).count()
        
        # Últimos despachos para las alertas
        ultimos_despachos = Despacho.objects.all().order_by('-fecha_despacho')[:6]
        
        # Seguros recientes
        seguros_recientes = Seguro.objects.all().order_by('-vigencia_hasta')[:3]
        
        # Cálculo de porcentajes
        total_flota = total_vehiculos + total_aeronaves
        porcentaje_vehiculos_activos = round((total_vehiculos / max(total_vehiculos, 1)) * 100) if total_vehiculos > 0 else 0
        porcentaje_aeronaves_activas = round((total_aeronaves / max(total_aeronaves, 1)) * 100) if total_aeronaves > 0 else 0
        porcentaje_personal_activo = round(((total_conductores + total_pilotos) / max(total_conductores + total_pilotos, 1)) * 100)
        
        # Calcular porcentaje de seguros vigentes
        seguros_vigentes = Seguro.objects.filter(vigencia_hasta__gte=timezone.now().date()).count()
        total_seguros = Seguro.objects.count()
        porcentaje_seguros_vigentes = round((seguros_vigentes / max(total_seguros, 1)) * 100) if total_seguros > 0 else 0
        
        context = {
            # Estadísticas principales
            'total_vehiculos': total_vehiculos,
            'total_aeronaves': total_aeronaves,
            'total_despachos': total_despachos,
            'total_clientes': total_clientes,
            'total_conductores': total_conductores,
            'total_pilotos': total_pilotos,
            
            # Datos para las secciones
            'ultimos_despachos': ultimos_despachos,
            'seguros_recientes': seguros_recientes,
            
            # Porcentajes calculados
            'porcentaje_vehiculos_activos': porcentaje_vehiculos_activos,
            'porcentaje_aeronaves_activas': porcentaje_aeronaves_activas,
            'porcentaje_personal_activo': porcentaje_personal_activo,
            'porcentaje_seguros_vigentes': porcentaje_seguros_vigentes,
            
            'tipo_usuario': tipo_usuario,
            'es_admin': True
        }
        return render(request, 'transporte/dashboard.html', context)
    
    else:
        # DASHBOARD PARA USUARIOS NO-ADMIN (CLIENTE, CONDUCTOR, PILOTO)
        return render(request, 'transporte/dashboard_usuario.html', {
            'tipo_usuario': tipo_usuario,
            'es_admin': False,
            'nombre_usuario': request.user.get_full_name() or request.user.username
        })

@login_required
@admin_required
def crear_despacho(request):
    """Vista para crear un nuevo despacho"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            cliente_id = request.POST.get('cliente')
            ruta_id = request.POST.get('ruta')
            carga_id = request.POST.get('carga')
            costo_envio = request.POST.get('costo_envio')
            estado = request.POST.get('estado')
            vehiculo_id = request.POST.get('vehiculo') or None
            aeronave_id = request.POST.get('aeronave') or None
            conductor_id = request.POST.get('conductor') or None
            piloto_id = request.POST.get('piloto') or None
            
            # Crear el despacho
            despacho = Despacho(
                cliente_id=cliente_id,
                ruta_id=ruta_id,
                carga_id=carga_id,
                costo_envio=costo_envio,
                estado=estado,
                vehiculo_id=vehiculo_id,
                aeronave_id=aeronave_id,
                conductor_id=conductor_id,
                piloto_id=piloto_id
            )
            despacho.save()
            
            messages.success(request, 'Despacho creado exitosamente')
            return redirect('despachos')
            
        except Exception as e:
            messages.error(request, f'Error al crear el despacho: {str(e)}')
    
    # Mostrar formulario para crear despacho
    context = {
        'rutas': Ruta.objects.all(),
        'vehiculos': Vehiculo.objects.filter(activo=True),
        'aeronaves': Aeronave.objects.filter(activo=True),
        'conductores': Conductor.objects.filter(activo=True),
        'pilotos': Piloto.objects.filter(activo=True),
        'cargas': Carga.objects.all(),
        'clientes': Cliente.objects.filter(activo=True),
    }
    return render(request, 'transporte/despacho_form.html', context)

@login_required
@admin_required
def eliminar_aeronave(request, pk):
    """Vista para eliminar una aeronave"""
    aeronave = get_object_or_404(Aeronave, pk=pk)
    
    if request.method == 'POST':
        try:
            aeronave.delete()
            messages.success(request, 'Aeronave eliminada exitosamente')
            return redirect('aeronaves')
        except Exception as e:
            messages.error(request, f'Error al eliminar la aeronave: {str(e)}')
    
    context = {'aeronave': aeronave}
    return render(request, 'transporte/aeronave_confirm_delete.html', context)

@login_required
def editar_despacho(request, pk):
    """Vista para editar un despacho existente"""
    despacho = get_object_or_404(Despacho, pk=pk)
    
    if request.method == 'POST':
        # Lógica para editar despacho
        messages.success(request, 'Despacho actualizado exitosamente')
        return redirect('despachos')
    else:
        # Mostrar formulario para editar despacho
        context = {
            'despacho': despacho,
            'rutas': Ruta.objects.all(),
            'vehiculos': Vehiculo.objects.filter(activo=True),
            'aeronaves': Aeronave.objects.filter(activo=True),
            'conductores': Conductor.objects.filter(activo=True),
            'pilotos': Piloto.objects.filter(activo=True),
            'cargas': Carga.objects.all(),
            'clientes': Cliente.objects.filter(activo=True),
        }
        return render(request, 'transporte/despacho_form.html', context)

@login_required
def despacho_detail(request, pk):
    """Vista para ver los detalles de un despacho"""
    despacho = get_object_or_404(Despacho, pk=pk)
    context = {
        'despacho': despacho,
    }
    return render(request, 'transporte/despacho_detail.html', context)

@login_required
def eliminar_despacho(request, pk):
    """Vista para eliminar un despacho"""
    despacho = get_object_or_404(Despacho, pk=pk)
    
    if request.method == 'POST':
        despacho.delete()
        messages.success(request, 'Despacho eliminado exitosamente')
        return redirect('despachos')
    
    context = {
        'despacho': despacho,
    }
    return render(request, 'transporte/despacho_confirm_delete.html', context)

@login_required
def despachos_view(request):
    # Obtener parámetros de filtro
    estado_filter = request.GET.get('estado', '')
    tipo_filter = request.GET.get('tipo', '')
    search_query = request.GET.get('search', '')
    
    # Filtrar despachos - ✅ CORREGIR ESTA LÍNEA
    despachos = Despacho.objects.all().order_by('-fecha_despacho')
    
    if estado_filter:
        despachos = despachos.filter(estado=estado_filter)
    
    if tipo_filter:
        if tipo_filter == 'terrestre':
            despachos = despachos.filter(vehiculo__isnull=False)
        elif tipo_filter == 'aereo':
            despachos = despachos.filter(aeronave__isnull=False)
    
    if search_query:
        despachos = despachos.filter(
            Q(cliente__razon_social__icontains=search_query) |
            Q(ruta__origen__icontains=search_query) |
            Q(ruta__destino__icontains=search_query) |
            Q(carga__descripcion__icontains=search_query)
        )
    
    context = {
        'despachos': despachos,
        'estado_filter': estado_filter,
        'tipo_filter': tipo_filter,
        'search_query': search_query,
        'total_despachos': despachos.count(),
    }
    return render(request, 'transporte/despachos.html', context)

@login_required
def rutas_view(request):
    rutas = Ruta.objects.all()
    return render(request, 'transporte/rutas.html', {'rutas': rutas})

@login_required
def vehiculos_view(request):
    # ✅ CARGAR DATOS RELACIONADOS
    vehiculos = Vehiculo.objects.select_related('conductor_asignado').all()
    
    try:
        if hasattr(request.user, 'perfilusuario'):
            solo_lectura_flag = request.user.perfilusuario.tipo_usuario != 'ADMIN'
        else:
            solo_lectura_flag = True
    except Exception as e:
        solo_lectura_flag = True
    
    return render(request, 'transporte/vehiculos.html', {
        'vehiculos': vehiculos,
        'solo_lectura': solo_lectura_flag
    })


@login_required
def aeronaves_view(request):
    # ✅ CARGAR DATOS RELACIONADOS
    aeronaves = Aeronave.objects.select_related('piloto_asignado').all()
    
    try:
        if hasattr(request.user, 'perfilusuario'):
            es_admin = request.user.perfilusuario.tipo_usuario == 'ADMIN'
        else:
            es_admin = False
    except:
        es_admin = False
    
    return render(request, 'transporte/aeronaves.html', {
        'aeronaves': aeronaves,
        'es_admin': es_admin
    })

@login_required
def conductores_view(request):
    conductores = Conductor.objects.all()
    return render(request, 'transporte/conductores.html', {'conductores': conductores})

@login_required
def pilotos_view(request):
    pilotos = Piloto.objects.all()
    return render(request, 'transporte/pilotos.html', {'pilotos': pilotos})

@login_required
def clientes_view(request):
    clientes = Cliente.objects.all()
    return render(request, 'transporte/clientes.html', {'clientes': clientes})

@login_required
def cargas_view(request):
    cargas = Carga.objects.all()
    return render(request, 'transporte/cargas.html', {'cargas': cargas})

@login_required
def seguros_view(request):
    seguros = Seguro.objects.all()
    return render(request, 'transporte/seguros.html', {'seguros': seguros})

@login_required
def api_view(request):
    """Vista para la documentación de la API"""
    return render(request, 'transporte/api.html')

@login_required
def reportes_view(request):
    # Datos para reportes
    despachos_por_estado = Despacho.objects.values('estado').annotate(total=Count('id'))
    cargas_por_tipo = Carga.objects.values('tipo_carga').annotate(total=Count('id'))
    ingresos_por_mes = Despacho.objects.extra(
        {'mes': "strftime('%%m', fecha_despacho)"}
    ).values('mes').annotate(total=Sum('costo_envio'))
    
    context = {
        'despachos_por_estado': despachos_por_estado,
        'cargas_por_tipo': cargas_por_tipo,
        'ingresos_por_mes': ingresos_por_mes,
    }
    return render(request, 'transporte/reportes.html', context)

@login_required
def editar_vehiculo(request, pk):
    """Vista para editar un vehículo existente"""
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    
    if request.method == 'POST':
        try:
            # Actualizar campos del vehículo
            vehiculo.patente = request.POST.get('patente')
            vehiculo.tipo_vehiculo = request.POST.get('tipo_vehiculo')
            vehiculo.modelo = request.POST.get('modelo')
            vehiculo.capacidad_kg = request.POST.get('capacidad_kg')
            vehiculo.año = request.POST.get('año')
            conductor_id = request.POST.get('conductor_asignado')
            vehiculo.conductor_asignado = Conductor.objects.get(pk=conductor_id) if conductor_id else None
            vehiculo.activo = 'activo' in request.POST
            
            vehiculo.save()
            messages.success(request, 'Vehículo actualizado exitosamente')
            return redirect('vehiculos')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar el vehículo: {str(e)}')
    
    context = {
        'vehiculo': vehiculo,
        'conductores': Conductor.objects.filter(activo=True),
    }
    return render(request, 'transporte/vehiculo_editar.html', context)

@login_required
def editar_aeronave(request, pk):
    """Vista para editar una aeronave existente"""
    aeronave = get_object_or_404(Aeronave, pk=pk)
    
    if request.method == 'POST':
        try:
            # Actualizar campos de la aeronave
            aeronave.matricula = request.POST.get('matricula')
            aeronave.tipo_aeronave = request.POST.get('tipo_aeronave')
            aeronave.modelo = request.POST.get('modelo')
            aeronave.capacidad_kg = request.POST.get('capacidad_kg')
            piloto_id = request.POST.get('piloto_asignado')
            aeronave.piloto_asignado = Piloto.objects.get(pk=piloto_id) if piloto_id else None
            aeronave.activo = 'activo' in request.POST
            
            aeronave.save()
            messages.success(request, 'Aeronave actualizada exitosamente')
            return redirect('aeronaves')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar la aeronave: {str(e)}')
    
    context = {
        'aeronave': aeronave,
        'pilotos': Piloto.objects.filter(activo=True),
    }
    return render(request, 'transporte/aeronave_editar.html', context)

@login_required
def editar_conductor(request, pk):
    """Vista para editar un conductor existente"""
    conductor = get_object_or_404(Conductor, pk=pk)
    
    if request.method == 'POST':
        try:
            # Actualizar campos del conductor
            conductor.nombre = request.POST.get('nombre')
            conductor.rut = request.POST.get('rut')
            conductor.licencia = request.POST.get('licencia')
            conductor.telefono = request.POST.get('telefono')
            conductor.email = request.POST.get('email')
            conductor.activo = 'activo' in request.POST
            
            conductor.save()
            messages.success(request, 'Conductor actualizado exitosamente')
            return redirect('conductores')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar el conductor: {str(e)}')
    
    context = {
        'conductor': conductor,
    }
    return render(request, 'transporte/conductor_editar.html', context)

@login_required
def editar_piloto(request, pk):
    """Vista para editar un piloto existente"""
    piloto = get_object_or_404(Piloto, pk=pk)
    
    if request.method == 'POST':
        try:
            # Actualizar campos del piloto
            piloto.nombre = request.POST.get('nombre')
            piloto.rut = request.POST.get('rut')
            piloto.certificacion = request.POST.get('certificacion')
            piloto.telefono = request.POST.get('telefono')
            piloto.email = request.POST.get('email')
            piloto.horas_vuelo = request.POST.get('horas_vuelo', 0)
            piloto.activo = 'activo' in request.POST
            
            piloto.save()
            messages.success(request, 'Piloto actualizado exitosamente')
            return redirect('pilotos')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar el piloto: {str(e)}')
    
    context = {
        'piloto': piloto,
    }
    return render(request, 'transporte/piloto_editar.html', context)

@login_required
def editar_cliente(request, pk):
    """Vista para editar un cliente existente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    
    if request.method == 'POST':
        try:
            # Actualizar campos del cliente
            cliente.tipo_cliente = request.POST.get('tipo_cliente')
            cliente.razon_social = request.POST.get('razon_social')
            cliente.nombre = request.POST.get('nombre')
            cliente.apellido = request.POST.get('apellido')
            cliente.rut = request.POST.get('rut')
            cliente.persona_contacto = request.POST.get('persona_contacto')
            cliente.telefono = request.POST.get('telefono')
            cliente.email = request.POST.get('email')
            cliente.direccion = request.POST.get('direccion')
            cliente.activo = 'activo' in request.POST
            
            cliente.save()
            messages.success(request, 'Cliente actualizado exitosamente')
            return redirect('clientes')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar el cliente: {str(e)}')
    
    context = {
        'cliente': cliente,
    }
    return render(request, 'transporte/cliente_editar.html', context)

@login_required
def vehiculo_detail(request, pk):
    """Vista para ver detalles de un vehículo"""
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    context = {
        'vehiculo': vehiculo,
    }
    return render(request, 'transporte/vehiculo_detail.html', context)

@login_required
def conductor_detail(request, pk):
    """Vista para ver detalles de un conductor"""
    conductor = get_object_or_404(Conductor, pk=pk)
    context = {
        'conductor': conductor,
    }
    return render(request, 'transporte/conductor_detail.html', context)

@login_required
def piloto_detail(request, pk):
    """Vista para ver detalles de un piloto"""
    piloto = get_object_or_404(Piloto, pk=pk)
    context = {
        'piloto': piloto,
    }
    return render(request, 'transporte/piloto_detail.html', context)

@login_required
def cliente_detail(request, pk):
    """Vista para ver detalles de un cliente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    context = {
        'cliente': cliente,
    }
    return render(request, 'transporte/cliente_detail.html', context)

@login_required
def carga_detail(request, pk):
    """Vista para ver detalles de una carga"""
    carga = get_object_or_404(Carga, pk=pk)
    context = {
        'carga': carga,
    }
    return render(request, 'transporte/carga_detail.html', context)

@login_required
def seguro_detail(request, pk):
    """Vista para ver detalles de un seguro"""
    seguro = get_object_or_404(Seguro, pk=pk)
    context = {
        'seguro': seguro,
    }
    return render(request, 'transporte/seguro_detail.html', context)

@login_required
def editar_carga(request, pk):
    """Vista para editar una carga existente"""
    carga = get_object_or_404(Carga, pk=pk)
    
    if request.method == 'POST':
        try:
            # Actualizar campos de la carga
            carga.descripcion = request.POST.get('descripcion')
            carga.tipo_carga = request.POST.get('tipo_carga')
            carga.peso_kg = request.POST.get('peso_kg')
            carga.volumen_m3 = request.POST.get('volumen_m3')
            carga.valor_declarado = request.POST.get('valor_declarado')
            carga.notas_especiales = request.POST.get('notas_especiales')
            cliente_id = request.POST.get('cliente')
            carga.cliente = Cliente.objects.get(pk=cliente_id) if cliente_id else None
            
            carga.save()
            messages.success(request, 'Carga actualizada exitosamente')
            return redirect('cargas')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar la carga: {str(e)}')
    
    context = {
        'carga': carga,
        'clientes': Cliente.objects.filter(activo=True),
    }
    return render(request, 'transporte/carga_editar.html', context)

@login_required
def editar_seguro(request, pk):
    """Vista para editar un seguro existente"""
    seguro = get_object_or_404(Seguro, pk=pk)
    
    if request.method == 'POST':
        try:
            # Actualizar campos del seguro
            seguro.numero_poliza = request.POST.get('numero_poliza')
            seguro.tipo_seguro = request.POST.get('tipo_seguro')
            seguro.aseguradora = request.POST.get('aseguradora')
            seguro.cobertura = request.POST.get('cobertura')
            seguro.vigencia_desde = request.POST.get('vigencia_desde')
            seguro.vigencia_hasta = request.POST.get('vigencia_hasta')
            seguro.estado = request.POST.get('estado')
            
            # Actualizar vehículo o aeronave
            vehiculo_id = request.POST.get('vehiculo')
            aeronave_id = request.POST.get('aeronave')
            
            seguro.vehiculo = Vehiculo.objects.get(pk=vehiculo_id) if vehiculo_id else None
            seguro.aeronave = Aeronave.objects.get(pk=aeronave_id) if aeronave_id else None
            
            seguro.save()
            messages.success(request, 'Seguro actualizado exitosamente')
            return redirect('seguros')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar el seguro: {str(e)}')
    
    context = {
        'seguro': seguro,
        'vehiculos': Vehiculo.objects.filter(activo=True),
        'aeronaves': Aeronave.objects.filter(activo=True),
    }
    return render(request, 'transporte/seguro_editar.html', context)

# Agrega estas vistas al final de tu views.py
@login_required
@admin_required
def crear_vehiculo(request):
    """Vista para crear un nuevo vehículo"""
    # ✅ CARGAR CONDUCTORES ACTIVOS - Misma lógica que en editar_vehiculo
    conductores = Conductor.objects.filter(activo=True)
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            patente = request.POST.get('patente')
            tipo_vehiculo = request.POST.get('tipo_vehiculo')
            modelo = request.POST.get('modelo')
            capacidad_kg = request.POST.get('capacidad_kg')
            año = request.POST.get('año')
            conductor_id = request.POST.get('conductor_asignado')
            activo = 'activo' in request.POST
            
            # Crear el vehículo
            vehiculo = Vehiculo(
                patente=patente,
                tipo_vehiculo=tipo_vehiculo,
                modelo=modelo,
                capacidad_kg=capacidad_kg,
                año=año,
                conductor_asignado_id=conductor_id if conductor_id else None,
                activo=activo
            )
            vehiculo.save()
            
            messages.success(request, 'Vehículo creado exitosamente')
            return redirect('vehiculos')
            
        except Exception as e:
            messages.error(request, f'Error al crear el vehículo: {str(e)}')
    
    context = {
        'conductores': conductores,
    }
    return render(request, 'transporte/vehiculo_form.html', context)

@login_required
@admin_required
def eliminar_vehiculo(request, pk):
    """Vista para eliminar un vehículo"""
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    
    if request.method == 'POST':
        try:
            vehiculo.delete()
            messages.success(request, 'Vehículo eliminado exitosamente')
            return redirect('vehiculos')
                
        except Exception as e:
            messages.error(request, f'Error al eliminar el vehículo: {str(e)}')
            return redirect('vehiculos')
    
    # Si es GET, mostrar confirmación
    context = {
        'vehiculo': vehiculo,
    }
    return render(request, 'transporte/vehiculo_confirm_delete.html', context)

@login_required
@admin_required
def crear_aeronave(request):
    """Vista para crear una nueva aeronave"""
    # ✅ CARGAR PILOTOS ACTIVOS CORRECTAMENTE
    pilotos = Piloto.objects.filter(activo=True)
    print(f"🔍 CREAR_AERONAVE - Pilotos en BD: {pilotos.count()}")
    for p in pilotos:
        print(f"   - {p.id}: {p.nombre}")
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            matricula = request.POST.get('matricula')[:10]
            tipo_aeronave = request.POST.get('tipo_aeronave')
            modelo = request.POST.get('modelo')
            capacidad_kg = request.POST.get('capacidad_kg')
            piloto_id = request.POST.get('piloto_asignado') or None
            activo = 'activo' in request.POST
            
            print(f"🔍 CREAR_AERONAVE - Datos recibidos:")
            print(f"   Matrícula: {matricula}")
            print(f"   Piloto ID: {piloto_id}")
            
            # Crear la aeronave
            aeronave = Aeronave(
                matricula=matricula,
                tipo_aeronave=tipo_aeronave,
                modelo=modelo,
                capacidad_kg=capacidad_kg,
                piloto_asignado_id=piloto_id,
                activo=activo
            )
            aeronave.save()
            
            messages.success(request, 'Aeronave creada exitosamente')
            return redirect('aeronaves')
            
        except Exception as e:
            print(f"❌ Error al crear aeronave: {str(e)}")
            messages.error(request, f'Error al crear la aeronave: {str(e)}')
    
    context = {
        'pilotos': pilotos,
    }
    return render(request, 'transporte/aeronave_form.html', context)

@login_required
@admin_required
def crear_conductor(request):
    """Vista para crear un nuevo conductor"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre = request.POST.get('nombre')
            rut = request.POST.get('rut')
            licencia = request.POST.get('licencia')
            telefono = request.POST.get('telefono')
            email = request.POST.get('email')
            activo = 'activo' in request.POST
            
            # Crear el conductor
            conductor = Conductor(
                nombre=nombre,
                rut=rut,
                licencia=licencia,
                telefono=telefono,
                email=email,
                activo=activo
            )
            conductor.save()
            
            messages.success(request, 'Conductor creado exitosamente')
            return redirect('conductores')
            
        except Exception as e:
            messages.error(request, f'Error al crear el conductor: {str(e)}')
    
    return render(request, 'transporte/conductor_form.html')

@login_required
@admin_required
def eliminar_conductor(request, pk):
    """Vista para eliminar un conductor"""
    conductor = get_object_or_404(Conductor, pk=pk)
    
    if request.method == 'POST':
        try:
            conductor.delete()
            messages.success(request, 'Conductor eliminado exitosamente')
            return redirect('conductores')
        except Exception as e:
            messages.error(request, f'Error al eliminar el conductor: {str(e)}')
    
    context = {'conductor': conductor}
    return render(request, 'transporte/conductor_confirm_delete.html', context)

@login_required
@admin_required
def crear_piloto(request):
    """Vista para crear un nuevo piloto"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre = request.POST.get('nombre')
            rut = request.POST.get('rut')
            certificacion = request.POST.get('certificacion')
            telefono = request.POST.get('telefono')
            email = request.POST.get('email')
            horas_vuelo = request.POST.get('horas_vuelo', 0)
            activo = 'activo' in request.POST
            
            # Crear el piloto
            piloto = Piloto(
                nombre=nombre,
                rut=rut,
                certificacion=certificacion,
                telefono=telefono,
                email=email,
                horas_vuelo=horas_vuelo,
                activo=activo
            )
            piloto.save()
            
            messages.success(request, 'Piloto creado exitosamente')
            return redirect('pilotos')
            
        except Exception as e:
            messages.error(request, f'Error al crear el piloto: {str(e)}')
    
    return render(request, 'transporte/piloto_form.html')

@login_required
@admin_required
def eliminar_piloto(request, pk):
    """Vista para eliminar un piloto"""
    piloto = get_object_or_404(Piloto, pk=pk)
    
    if request.method == 'POST':
        try:
            piloto.delete()
            messages.success(request, 'Piloto eliminado exitosamente')
            return redirect('pilotos')
        except Exception as e:
            messages.error(request, f'Error al eliminar el piloto: {str(e)}')
    
    context = {'piloto': piloto}
    return render(request, 'transporte/piloto_confirm_delete.html', context)

@login_required
@admin_required
def crear_cliente(request):
    """Vista para crear un nuevo cliente"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            tipo_cliente = request.POST.get('tipo_cliente')
            razon_social = request.POST.get('razon_social')
            nombre = request.POST.get('nombre')
            apellido = request.POST.get('apellido')
            rut = request.POST.get('rut')
            persona_contacto = request.POST.get('persona_contacto')
            telefono = request.POST.get('telefono')
            email = request.POST.get('email')
            direccion = request.POST.get('direccion')
            activo = 'activo' in request.POST
            
            # Crear el cliente
            cliente = Cliente(
                tipo_cliente=tipo_cliente,
                razon_social=razon_social,
                nombre=nombre,
                apellido=apellido,
                rut=rut,
                persona_contacto=persona_contacto,
                telefono=telefono,
                email=email,
                direccion=direccion,
                activo=activo
            )
            cliente.save()
            
            messages.success(request, 'Cliente creado exitosamente')
            return redirect('clientes')
            
        except Exception as e:
            messages.error(request, f'Error al crear el cliente: {str(e)}')
    
    return render(request, 'transporte/cliente_form.html')

@login_required
@admin_required
def eliminar_cliente(request, pk):
    """Vista para eliminar un cliente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    
    if request.method == 'POST':
        try:
            cliente.delete()
            messages.success(request, 'Cliente eliminado exitosamente')
            return redirect('clientes')
        except Exception as e:
            messages.error(request, f'Error al eliminar el cliente: {str(e)}')
    
    context = {'cliente': cliente}
    return render(request, 'transporte/cliente_confirm_delete.html', context)

@login_required
@admin_required
def crear_carga(request):
    """Vista para crear una nueva carga"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            descripcion = request.POST.get('descripcion')
            tipo_carga = request.POST.get('tipo_carga')
            peso_kg = request.POST.get('peso_kg')
            volumen_m3 = request.POST.get('volumen_m3')
            valor_declarado = request.POST.get('valor_declarado')
            cliente_id = request.POST.get('cliente')
            notas_especiales = request.POST.get('notas_especiales', '')
            
            # Crear la carga
            carga = Carga(
                descripcion=descripcion,
                tipo_carga=tipo_carga,
                peso_kg=peso_kg,
                volumen_m3=volumen_m3,
                valor_declarado=valor_declarado,
                cliente_id=cliente_id,
                notas_especiales=notas_especiales
            )
            carga.save()
            
            messages.success(request, 'Carga creada exitosamente')
            return redirect('cargas')
            
        except Exception as e:
            messages.error(request, f'Error al crear la carga: {str(e)}')
    
    # Mostrar formulario para crear carga
    context = {
        'clientes': Cliente.objects.filter(activo=True),
    }
    return render(request, 'transporte/carga_form.html', context)

@login_required
@admin_required
def eliminar_carga(request, pk):
    """Vista para eliminar una carga"""
    carga = get_object_or_404(Carga, pk=pk)
    
    if request.method == 'POST':
        try:
            carga.delete()
            messages.success(request, 'Carga eliminada exitosamente')
            return redirect('cargas')
        except Exception as e:
            messages.error(request, f'Error al eliminar la carga: {str(e)}')
    
    context = {'carga': carga}
    return render(request, 'transporte/carga_confirm_delete.html', context)

@login_required
@admin_required
def crear_seguro(request):
    """Vista para crear un nuevo seguro"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            numero_poliza = request.POST.get('numero_poliza')
            tipo_seguro = request.POST.get('tipo_seguro')
            aseguradora = request.POST.get('aseguradora')
            cobertura = request.POST.get('cobertura')
            vigencia_desde = request.POST.get('vigencia_desde')
            vigencia_hasta = request.POST.get('vigencia_hasta')
            estado = request.POST.get('estado')
            vehiculo_id = request.POST.get('vehiculo') or None
            aeronave_id = request.POST.get('aeronave') or None
            
            # Crear el seguro
            seguro = Seguro(
                numero_poliza=numero_poliza,
                tipo_seguro=tipo_seguro,
                aseguradora=aseguradora,
                cobertura=cobertura,
                vigencia_desde=vigencia_desde,
                vigencia_hasta=vigencia_hasta,
                estado=estado,
                vehiculo_id=vehiculo_id,
                aeronave_id=aeronave_id
            )
            seguro.save()
            
            messages.success(request, 'Seguro creado exitosamente')
            return redirect('seguros')
            
        except Exception as e:
            messages.error(request, f'Error al crear el seguro: {str(e)}')
    
    # Mostrar formulario para crear seguro
    context = {
        'vehiculos': Vehiculo.objects.filter(activo=True),
        'aeronaves': Aeronave.objects.filter(activo=True),
    }
    return render(request, 'transporte/seguro_form.html', context)


@login_required
@admin_required
def eliminar_seguro(request, pk):
    """Vista para eliminar un seguro"""
    seguro = get_object_or_404(Seguro, pk=pk)
    
    if request.method == 'POST':
        try:
            seguro.delete()
            messages.success(request, 'Seguro eliminado exitosamente')
            return redirect('seguros')
        except Exception as e:
            messages.error(request, f'Error al eliminar el seguro: {str(e)}')
    
    context = {'seguro': seguro}
    return render(request, 'transporte/seguro_confirm_delete.html', context)

# En transporte/views.py - AGREGAR AL FINAL DEL ARCHIVO

from rest_framework.response import Response

# ✅ VISTAS API ESPECÍFICAS PARA DATOS REALES
@drf_api_view(['GET'])
@permission_classes([permissions.AllowAny])  # Acceso público
def api_rutas_list(request):
    """API para obtener lista de rutas"""
    rutas = Ruta.objects.all()
    serializer = RutaSerializer(rutas, many=True)
    return Response(serializer.data)

@drf_api_view(['GET'])
@permission_classes([permissions.AllowAny])  # Acceso público
def api_vehiculos_list(request):
    """API para obtener lista de vehículos"""
    vehiculos = Vehiculo.objects.filter(activo=True)
    serializer = VehiculoSerializer(vehiculos, many=True)
    return Response(serializer.data)

@drf_api_view(['GET'])
@permission_classes([permissions.AllowAny])  # Acceso público
def api_aeronaves_list(request):
    """API para obtener lista de aeronaves"""
    aeronaves = Aeronave.objects.filter(activo=True)
    serializer = AeronaveSerializer(aeronaves, many=True)
    return Response(serializer.data)

@drf_api_view(['GET'])
@permission_classes([permissions.AllowAny])  # Acceso público
def api_conductores_list(request):
    """API para obtener lista de conductores"""
    conductores = Conductor.objects.filter(activo=True)
    serializer = ConductorSerializer(conductores, many=True)
    return Response(serializer.data)

@drf_api_view(['GET'])
@permission_classes([permissions.AllowAny])  # Acceso público
def api_pilotos_list(request):
    """API para obtener lista de pilotos"""
    pilotos = Piloto.objects.filter(activo=True)
    serializer = PilotoSerializer(pilotos, many=True)
    return Response(serializer.data)

@drf_api_view(['GET'])
@permission_classes([permissions.AllowAny])  # Acceso público
def api_clientes_list(request):
    """API para obtener lista de clientes"""
    clientes = Cliente.objects.filter(activo=True)
    serializer = ClienteSerializer(clientes, many=True)
    return Response(serializer.data)

@drf_api_view(['GET'])
@permission_classes([permissions.AllowAny])  # Acceso público
def api_cargas_list(request):
    """API para obtener lista de cargas"""
    cargas = Carga.objects.all()
    serializer = CargaSerializer(cargas, many=True)
    return Response(serializer.data)

@drf_api_view(['GET'])
@permission_classes([permissions.AllowAny])  # Acceso público
def api_seguros_list(request):
    """API para obtener lista de seguros"""
    seguros = Seguro.objects.all()
    serializer = SeguroSerializer(seguros, many=True)
    return Response(serializer.data)

@drf_api_view(['GET'])
@permission_classes([permissions.AllowAny])  # Acceso público
def api_despachos_list(request):
    """API para obtener lista de despachos"""
    despachos = Despacho.objects.all().order_by('-fecha_despacho')[:50]
    serializer = DespachoSerializer(despachos, many=True)
    return Response(serializer.data)

@login_required
def aeronave_detail(request, pk):
    """Vista para ver detalles de una aeronave"""
    aeronave = get_object_or_404(Aeronave, pk=pk)
    context = {
        'aeronave': aeronave,
    }
    return render(request, 'transporte/aeronave_detail.html', context)

@login_required
def debug_user_info(request):
    """Vista temporal para diagnóstico de permisos"""
    user_info = {
        'username': request.user.username,
        'is_superuser': request.user.is_superuser,
        'is_staff': request.user.is_staff,
        'is_authenticated': request.user.is_authenticated,
    }
    
    try:
        if hasattr(request.user, 'perfilusuario'):
            user_info['tipo_usuario'] = request.user.perfilusuario.tipo_usuario
            user_info['perfil_existe'] = True
            user_info['perfil_id'] = request.user.perfilusuario.id
        else:
            user_info['tipo_usuario'] = 'Sin perfil'
            user_info['perfil_existe'] = False
    except Exception as e:
        user_info['error'] = str(e)
    
    # También imprimir en consola para ver en tiempo real
    print("=" * 50)
    print("🔍 DIAGNÓSTICO DE USUARIO:")
    print(f"Usuario: {user_info['username']}")
    print(f"Superuser: {user_info['is_superuser']}")
    print(f"Staff: {user_info['is_staff']}")
    print(f"Tipo Usuario: {user_info.get('tipo_usuario', 'No disponible')}")
    print(f"Perfil existe: {user_info.get('perfil_existe', False)}")
    print("=" * 50)
    
    return JsonResponse(user_info)