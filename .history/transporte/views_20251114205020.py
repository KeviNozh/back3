from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import viewsets
from .models import *
from .serializers import *
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from datetime import datetime
import io
from django.http import JsonResponse
import json
from .decorators import admin_required, solo_lectura


# Vistas para API
class RutaViewSet(viewsets.ModelViewSet):
    queryset = Ruta.objects.all()
    serializer_class = RutaSerializer

class VehiculoViewSet(viewsets.ModelViewSet):
    queryset = Vehiculo.objects.all()
    serializer_class = VehiculoSerializer

class AeronaveViewSet(viewsets.ModelViewSet):
    queryset = Aeronave.objects.all()
    serializer_class = AeronaveSerializer

class ConductorViewSet(viewsets.ModelViewSet):
    queryset = Conductor.objects.all()
    serializer_class = ConductorSerializer

class PilotoViewSet(viewsets.ModelViewSet):
    queryset = Piloto.objects.all()
    serializer_class = PilotoSerializer

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

class CargaViewSet(viewsets.ModelViewSet):
    queryset = Carga.objects.all()
    serializer_class = CargaSerializer

class SeguroViewSet(viewsets.ModelViewSet):
    queryset = Seguro.objects.all()
    serializer_class = SeguroSerializer

class DespachoViewSet(viewsets.ModelViewSet):
    queryset = Despacho.objects.all()
    serializer_class = DespachoSerializer

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
            
            # Autenticar y loguear al usuario
            user = authenticate(username=username, password=password1)
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Cuenta creada exitosamente! Bienvenido {user.first_name}')
                return redirect('dashboard')
                
        except Exception as e:
            messages.error(request, 'Error al crear la cuenta')
    
    return render(request, 'transporte/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente')
    return redirect('login')

# Vistas para templates HTML (funciones)
# En transporte/views.py
@login_required
def dashboard(request):
    try:
        tipo_usuario = request.user.perfilusuario.tipo_usuario
    except:
        tipo_usuario = 'CLIENTE'

    context = {'tipo_usuario': tipo_usuario}

    if tipo_usuario == 'ADMIN':
        # Estadísticas completas para admin
        context.update({
            'total_vehiculos': Vehiculo.objects.filter(activo=True).count(),
            'total_aeronaves': Aeronave.objects.filter(activo=True).count(),
            'total_despachos': Despacho.objects.count(),
            # ... más estadísticas
        })
    elif tipo_usuario == 'CLIENTE':
        # Solo información relevante para clientes
        cliente = Cliente.objects.filter(usuario=request.user).first()
        if cliente:
            context.update({
                'mis_despachos': Despacho.objects.filter(cliente=cliente).count(),
                'despachos_pendientes': Despacho.objects.filter(cliente=cliente, estado='PENDIENTE').count(),
            })
    elif tipo_usuario == 'CONDUCTOR':
        # Información para conductores
        conductor = Conductor.objects.filter(usuario=request.user).first()
        if conductor:
            context.update({
                'mis_viajes': Despacho.objects.filter(conductor=conductor).count(),
                'viajes_pendientes': Despacho.objects.filter(conductor=conductor, estado='PENDIENTE').count(),
            })
    elif tipo_usuario == 'PILOTO':
        # Información para pilotos
        piloto = Piloto.objects.filter(usuario=request.user).first()
        if piloto:
            context.update({
                'mis_vuelos': Despacho.objects.filter(piloto=piloto).count(),
                'vuelos_pendientes': Despacho.objects.filter(piloto=piloto, estado='PENDIENTE').count(),
            })

    return render(request, 'transporte/dashboard.html', context)

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
def eliminar_aeronave(request, pk):
    """Vista para eliminar una aeronave"""
    aeronave = get_object_or_404(Aeronave, pk=pk)
    
    if request.method == 'POST':
        try:
            aeronave.delete()
            messages.success(request, 'Aeronave eliminada exitosamente')
            
            # Si es una solicitud AJAX, devolver JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Aeronave eliminada exitosamente'})
            else:
                return redirect('aeronaves')
                
        except Exception as e:
            error_msg = f'Error al eliminar la aeronave: {str(e)}'
            messages.error(request, error_msg)
            
            # Si es una solicitud AJAX, devolver JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': error_msg})
            else:
                return redirect('aeronaves')
    
    # Si es GET, mostrar confirmación
    context = {
        'aeronave': aeronave,
    }
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
    
    # Filtrar despachos
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
@solo_lectura
def vehiculos_view(request):
    """Todos pueden ver, pero solo admin puede editar"""
    vehiculos = Vehiculo.objects.all()
    return render(request, 'transporte/vehiculos.html', {
        'vehiculos': vehiculos,
        'solo_lectura': request.user.perfilusuario.tipo_usuario != 'ADMIN'
    })

@login_required
def aeronaves_view(request):
    aeronaves = Aeronave.objects.all()
    return render(request, 'transporte/aeronaves.html', {'aeronaves': aeronaves})

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