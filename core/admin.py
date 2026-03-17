from django.contrib import admin
from .models import Culto, Departamento, Ministerio


@admin.register(Ministerio)
class MinisterioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'local', 'lider', 'ativo', 'destaque', 'ordem')
    list_filter = ('ativo', 'destaque')
    search_fields = ('nome', 'local', 'lider', 'slug')
    prepopulated_fields = {'slug': ('nome',)}
    ordering = ('ordem', 'nome')


@admin.register(Culto)
class CultoAdmin(admin.ModelAdmin):
    list_display = ('ministerio', 'dia', 'horario', 'ativo', 'ordem')
    list_filter = ('ativo', 'dia', 'ministerio')
    search_fields = ('ministerio__nome', 'dia', 'horario', 'descricao')
    ordering = ('ministerio', 'ordem', 'id')


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ministerio', 'lider', 'ativo', 'ordem')
    list_filter = ('ativo', 'ministerio')
    search_fields = ('nome', 'ministerio__nome', 'lider')
    ordering = ('ministerio', 'ordem', 'nome')