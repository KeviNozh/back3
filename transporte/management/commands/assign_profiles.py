# transporte/management/commands/assign_profiles.py
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from transporte.models import PerfilUsuario, TipoUsuario

class Command(BaseCommand):
    help = 'Asigna perfiles a usuarios existentes'

    def handle(self, *args, **options):
        for user in User.objects.all():
            if not hasattr(user, 'perfilusuario'):
                PerfilUsuario.objects.create(
                    usuario=user,
                    tipo_usuario=TipoUsuario.ADMIN if user.is_staff else TipoUsuario.CLIENTE
                )
                self.stdout.write(self.style.SUCCESS(f'Perfil creado para {user.username}'))