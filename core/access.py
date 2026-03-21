from django.core.exceptions import PermissionDenied

from .models import Ministerio, PerfilAcesso


ADMIN_GERAL = PerfilAcesso.ESCOPO_ADMIN_GERAL
ADMIN_IGREJA = PerfilAcesso.ESCOPO_ADMIN_IGREJA


def get_user_profile(user):
    if not user or not user.is_authenticated:
        return None

    profile, _ = PerfilAcesso.objects.get_or_create(user=user)
    return profile


def user_can_manage_all(user):
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    profile = get_user_profile(user)
    return profile is not None and profile.escopo == ADMIN_GERAL


def get_user_ministerio(user):
    profile = get_user_profile(user)
    if profile is None:
        return None
    return profile.ministerio


def get_allowed_ministerios(user):
    if user_can_manage_all(user):
        return Ministerio.objects.all()

    ministerio = get_user_ministerio(user)
    if ministerio is None:
        return Ministerio.objects.none()

    return Ministerio.objects.filter(pk=ministerio.pk)


def ensure_user_has_ministerio(user):
    if user_can_manage_all(user):
        return None

    ministerio = get_user_ministerio(user)
    if ministerio is None:
        raise PermissionDenied(
            'Seu usuário não está vinculado a nenhuma igreja. Peça ao administrador para configurar o acesso.'
        )

    return ministerio


def ensure_user_can_access_ministerio(user, ministerio):
    if user_can_manage_all(user):
        return ministerio

    user_ministerio = ensure_user_has_ministerio(user)
    if ministerio.pk != user_ministerio.pk:
        raise PermissionDenied('Você não tem permissão para acessar os dados de outra igreja.')

    return ministerio
