from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import PerfilAcesso, RegistroAuditoria

User = get_user_model()


@receiver(post_save, sender=User)
def criar_perfil_acesso(sender, instance, created, **kwargs):
    if created:
        PerfilAcesso.objects.get_or_create(user=instance)


@receiver(user_logged_in)
def registrar_login(sender, request, user, **kwargs):
    ministerio = getattr(getattr(user, 'perfil_acesso', None), 'ministerio', None)
    RegistroAuditoria.objects.create(
        user=user,
        ministerio=ministerio,
        acao=RegistroAuditoria.ACAO_LOGIN,
        entidade='Autenticação',
        descricao='Entrou no painel administrativo.',
    )
