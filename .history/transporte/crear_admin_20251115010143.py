# crear_admin.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logistica.settings')
django.setup()

from django.contrib.auth.models import User
from transporte.models import PerfilUsuario

def crear_superusuario():
    """Crear superusuario si no existe"""
    try:
        if not User.objects.filter(username='admin').exists():
            user = User.objects.create_superuser(
                username='admin',
                email='admin@logistica.com',
                password='admin123',
                first_name='Administrador',
                last_name='Sistema'
            )
            
            # Crear perfil para el admin
            PerfilUsuario.objects.create(
                usuario=user,
                tipo_usuario='ADMIN',
                telefono='+56912345678',
                departamento='Administración'
            )
            
            print("✅ Superusuario creado:")
            print("   Usuario: admin")
            print("   Password: admin123")
            print("   Email: admin@logistica.com")
        else:
            print("ℹ️  El usuario admin ya existe")
            
    except Exception as e:
        print(f"❌ Error creando superusuario: {e}")

def crear_usuario_cliente():
    """Crear usuario cliente de prueba"""
    try:
        if not User.objects.filter(username='cliente').exists():
            user = User.objects.create_user(
                username='cliente',
                email='cliente@empresa.com',
                password='cliente123',
                first_name='Juan',
                last_name='Cliente'
            )
            
            # Crear perfil para el cliente
            PerfilUsuario.objects.create(
                usuario=user,
                tipo_usuario='CLIENTE',
                telefono='+56987654321',
                departamento='Ventas'
            )
            
            print("✅ Usuario cliente creado:")
            print("   Usuario: cliente")
            print("   Password: cliente123")
        else:
            print("ℹ️  El usuario cliente ya existe")
            
    except Exception as e:
        print(f"❌ Error creando usuario cliente: {e}")

if __name__ == '__main__':
    print("🚀 Creando usuarios del sistema...")
    crear_superusuario()
    crear_usuario_cliente()
    print("🎉 Proceso completado!")