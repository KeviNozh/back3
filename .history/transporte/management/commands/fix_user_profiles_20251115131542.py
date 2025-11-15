from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from transporte.models import PerfilUsuario

class Command(BaseCommand):
    help = 'Corrige los perfiles de usuario para superusuarios'

    def handle(self, *args, **options):
        # Para todos los superusuarios
        superusers = User.objects.filter(is_superuser=True)
        
        for user in superusers:
            try:
                perfil = user.perfilusuario
                if perfil.tipo_usuario != 'ADMIN':
                    perfil.tipo_usuario = 'ADMIN'
                    perfil.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'Perfil actualizado para superusuario: {user.username}')
                    )
            except PerfilUsuario.DoesNotExist:
                # Crear perfil para superusuario
                PerfilUsuario.objects.create(
                    usuario=user,
                    tipo_usuario='ADMIN'
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Perfil creado para superusuario: {user.username}')
                )
        
        # Para usuarios staff que no son superusuarios
        staff_users = User.objects.filter(is_staff=True, is_superuser=False)
        for user in staff_users:
            try:
                perfil = user.perfilusuario
                if perfil.tipo_usuario != 'ADMIN':
                    perfil.tipo_usuario = 'ADMIN'
                    perfil.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'Perfil actualizado para staff: {user.username}')
                    )
            except PerfilUsuario.DoesNotExist:
                PerfilUsuario.objects.create(
                    usuario=user,
                    tipo_usuario='ADMIN'
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Perfil creado para staff: {user.username}')
                )