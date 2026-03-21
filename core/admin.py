from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import Culto, Departamento, Evento, Ministerio, PerfilAcesso, RegistroAuditoria

User = get_user_model()


class PerfilAcessoInline(admin.StackedInline):
    model = PerfilAcesso
    can_delete = False
    extra = 0
    autocomplete_fields = ('ministerio',)
    fieldsets = (
        (
            'Acesso por igreja',
            {
                'fields': ('escopo', 'ministerio', 'observacoes'),
                'description': 'Defina se o usuário administra tudo ou apenas a igreja vinculada.',
            },
        ),
    )


try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = (PerfilAcessoInline,)


@admin.register(Ministerio)
class MinisterioAdmin(admin.ModelAdmin):
    list_display = (
        'nome',
        'local',
        'pastor_nome',
        'pastora_nome',
        'ativo',
        'destaque',
        'ordem',
    )
    list_filter = ('ativo', 'destaque')
    search_fields = (
        'nome',
        'local',
        'pastor_nome',
        'pastora_nome',
        'slug',
    )
    prepopulated_fields = {'slug': ('nome',)}
    ordering = ('ordem', 'nome')


@admin.register(Culto)
class CultoAdmin(admin.ModelAdmin):
    list_display = ('ministerio', 'dia', 'horario', 'ativo', 'ordem')
    list_filter = ('ativo', 'dia', 'ministerio')
    search_fields = ('ministerio__nome', 'dia', 'horario', 'descricao')
    ordering = ('ministerio', 'ordem', 'id')
    autocomplete_fields = ('ministerio',)


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = (
        'nome',
        'ministerio',
        'lider_nome',
        'lider_nome_esposa',
        'ativo',
        'ordem',
    )
    list_filter = ('ativo', 'ministerio')
    search_fields = (
        'nome',
        'ministerio__nome',
        'lider_nome',
        'lider_nome_esposa',
    )
    ordering = ('ministerio', 'ordem', 'nome')
    autocomplete_fields = ('ministerio',)


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'ministerio', 'publico', 'gratuito', 'data', 'ativo', 'destaque')
    list_filter = ('tipo', 'publico', 'gratuito', 'ativo', 'destaque', 'ministerio')
    search_fields = ('titulo', 'slug', 'ministerio__nome', 'local')
    ordering = ('data', 'titulo')
    autocomplete_fields = ('ministerio',)


@admin.register(PerfilAcesso)
class PerfilAcessoAdmin(admin.ModelAdmin):
    list_display = ('user', 'escopo', 'ministerio', 'atualizado_em')
    list_filter = ('escopo', 'ministerio')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'ministerio__nome')
    autocomplete_fields = ('user', 'ministerio')


@admin.register(RegistroAuditoria)
class RegistroAuditoriaAdmin(admin.ModelAdmin):
    list_display = ('criado_em', 'user', 'acao', 'entidade', 'ministerio', 'registro_id')
    list_filter = ('acao', 'entidade', 'ministerio')
    search_fields = ('user__username', 'descricao', 'entidade')
    autocomplete_fields = ('user', 'ministerio')
    readonly_fields = ('criado_em',)
