from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User

class TipoTransporte(models.TextChoices):
    TERRESTRE = 'TERRESTRE', 'Terrestre'
    AEREO = 'AEREO', 'Aéreo'

class EstadoDespacho(models.TextChoices):
    PENDIENTE = 'PENDIENTE', 'Pendiente'
    EN_RUTA = 'EN_RUTA', 'En Ruta'
    ENTREGADO = 'ENTREGADO', 'Entregado'
    CANCELADO = 'CANCELADO', 'Cancelado'

class Ruta(models.Model):
    origen = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)
    tipo_transporte = models.CharField(max_length=10, choices=TipoTransporte.choices)
    distancia_km = models.FloatField(validators=[MinValueValidator(0)])
    
    def __str__(self):
        return f"{self.origen} - {self.destino}"

class Vehiculo(models.Model):
    patente = models.CharField(max_length=10, unique=True)
    tipo_vehiculo = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    capacidad_kg = models.IntegerField(validators=[MinValueValidator(0)])
    año = models.IntegerField()
    conductor_asignado = models.ForeignKey('Conductor', on_delete=models.SET_NULL, null=True, blank=True)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.patente} - {self.modelo}"

class Aeronave(models.Model):
    matricula = models.CharField(max_length=10, unique=True)
    tipo_aeronave = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    capacidad_kg = models.IntegerField(validators=[MinValueValidator(0)])
    piloto_asignado = models.ForeignKey('Piloto', on_delete=models.SET_NULL, null=True, blank=True)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.matricula} - {self.modelo}"

class Conductor(models.Model):
    nombre = models.CharField(max_length=100)
    rut = models.CharField(max_length=12, unique=True)
    licencia = models.CharField(max_length=10)
    telefono = models.CharField(max_length=15)
    email = models.EmailField()
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.nombre} ({self.licencia})"

class Piloto(models.Model):
    nombre = models.CharField(max_length=100)
    rut = models.CharField(max_length=12, unique=True)
    certificacion = models.CharField(max_length=20)
    telefono = models.CharField(max_length=15)
    email = models.EmailField()
    horas_vuelo = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.nombre} ({self.certificacion})"

class Cliente(models.Model):
    TIPO_CLIENTE_CHOICES = [
        ('EMPRESA', 'Empresa'),
        ('INDIVIDUAL', 'Individual'),
    ]
    
    tipo_cliente = models.CharField(max_length=10, choices=TIPO_CLIENTE_CHOICES, default='EMPRESA')
    razon_social = models.CharField(max_length=200, blank=True, null=True)
    nombre = models.CharField(max_length=100, blank=True, null=True)
    apellido = models.CharField(max_length=100, blank=True, null=True)
    rut = models.CharField(max_length=12, unique=True)
    persona_contacto = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)
    email = models.EmailField()
    direccion = models.TextField()
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        if self.tipo_cliente == 'EMPRESA':
            return self.razon_social
        else:
            return f"{self.nombre} {self.apellido}"

class Carga(models.Model):
    descripcion = models.CharField(max_length=200)
    tipo_carga = models.CharField(max_length=50)
    peso_kg = models.FloatField(validators=[MinValueValidator(0)])
    volumen_m3 = models.FloatField(validators=[MinValueValidator(0)])
    valor_declarado = models.DecimalField(max_digits=12, decimal_places=2)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    notas_especiales = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.descripcion} - {self.cliente}"

class Seguro(models.Model):
    numero_poliza = models.CharField(max_length=50, unique=True)
    tipo_seguro = models.CharField(max_length=50)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, null=True, blank=True)
    aeronave = models.ForeignKey(Aeronave, on_delete=models.CASCADE, null=True, blank=True)
    aseguradora = models.CharField(max_length=100)
    cobertura = models.DecimalField(max_digits=12, decimal_places=2)
    vigencia_desde = models.DateField()
    vigencia_hasta = models.DateField()
    estado = models.CharField(max_length=20)
    
    def __str__(self):
        return f"{self.numero_poliza} - {self.aseguradora}"

class Despacho(models.Model):
    fecha_despacho = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=10, choices=EstadoDespacho.choices, default=EstadoDespacho.PENDIENTE)
    costo_envio = models.DecimalField(max_digits=10, decimal_places=2)
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.SET_NULL, null=True, blank=True)
    aeronave = models.ForeignKey(Aeronave, on_delete=models.SET_NULL, null=True, blank=True)
    conductor = models.ForeignKey(Conductor, on_delete=models.SET_NULL, null=True, blank=True)
    piloto = models.ForeignKey(Piloto, on_delete=models.SET_NULL, null=True, blank=True)
    carga = models.ForeignKey(Carga, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Despacho {self.id} - {self.ruta}"

# Modelo adicional para extender el usuario de Django (OPCIONAL)
class TipoUsuario(models.TextChoices):
    ADMIN = 'ADMIN', 'Administrador'
    CLIENTE = 'CLIENTE', 'Cliente'
    CONDUCTOR = 'CONDUCTOR', 'Conductor'
    PILOTO = 'PILOTO', 'Piloto'

class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=15, blank=True)
    departamento = models.CharField(max_length=50, blank=True)
    tipo_usuario = models.CharField(
        max_length=10, 
        choices=TipoUsuario.choices, 
        default=TipoUsuario.CLIENTE
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Perfil de {self.usuario.username} ({self.tipo_usuario})"

