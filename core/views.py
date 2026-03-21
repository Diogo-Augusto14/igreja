import calendar
from datetime import date

from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .access import (
    ensure_user_can_access_ministerio,
    ensure_user_has_ministerio,
    get_allowed_ministerios,
    get_user_ministerio,
    user_can_manage_all,
)
from .forms import (
    CultoForm,
    CultoInlineFormSet,
    DepartamentoForm,
    DepartamentoInlineFormSet,
    EventoForm,
    MinisterioForm,
)
from .models import Culto, Departamento, Evento, Ministerio, RegistroAuditoria


class PainelLoginView(auth_views.LoginView):
    template_name = 'login.html'

    def get_success_url(self):
        return self.get_redirect_url() or '/painel/'


def registrar_auditoria(user, acao, entidade, registro=None, ministerio=None, descricao=''):
    RegistroAuditoria.objects.create(
        user=user,
        ministerio=ministerio,
        acao=acao,
        entidade=entidade,
        registro_id=getattr(registro, 'pk', None),
        descricao=descricao,
    )


# =========================
# SITE PÚBLICO
# =========================

def home(request):
    return render(request, 'home.html', {})


def ministerio(request):
    ministerios = Ministerio.objects.filter(ativo=True).order_by('ordem', 'nome')

    contexto = {
        'ministerios': ministerios,
    }
    return render(request, 'ministerio.html', contexto)


def eventos(request):
    ministerio_id = request.GET.get('ministerio', '').strip()
    apenas_gratuitos = request.GET.get('gratuito', '').strip() == '1'
    publico = request.GET.get('publico', '').strip()

    ministerios = Ministerio.objects.filter(ativo=True).order_by('ordem', 'nome')

    eventos_qs = Evento.objects.filter(ativo=True)

    # Exibicao padrao: somente eventos gerais.
    if not ministerio_id:
        eventos_qs = eventos_qs.filter(tipo='geral')
    else:
        eventos_qs = eventos_qs.filter(Q(tipo='geral') | Q(tipo='local', ministerio_id=ministerio_id))

    if apenas_gratuitos:
        eventos_qs = eventos_qs.filter(gratuito=True)

    if publico:
        eventos_qs = eventos_qs.filter(publico=publico)

    eventos_qs = eventos_qs.select_related('ministerio').order_by('data', 'titulo')

    contexto = {
        'eventos': eventos_qs,
        'ministerios': ministerios,
        'ministerio_id': ministerio_id,
        'apenas_gratuitos': apenas_gratuitos,
        'publico': publico,
        'publico_choices': Evento.PUBLICO_CHOICES,
    }
    return render(request, 'eventos.html', contexto)


def detalhe_ministerio(request, slug):
    ministerio = get_object_or_404(
        Ministerio.objects.prefetch_related('cultos', 'departamentos', 'eventos'),
        slug=slug,
        ativo=True,
    )

    hoje = date.today()
    ano = hoje.year
    mes = hoje.month

    nomes_meses = {
        1: 'Janeiro',
        2: 'Fevereiro',
        3: 'Março',
        4: 'Abril',
        5: 'Maio',
        6: 'Junho',
        7: 'Julho',
        8: 'Agosto',
        9: 'Setembro',
        10: 'Outubro',
        11: 'Novembro',
        12: 'Dezembro',
    }

    eventos = Evento.objects.filter(ativo=True).filter(
        Q(tipo='geral') | Q(tipo='local', ministerio=ministerio)
    ).order_by('data')

    eventos_mes = eventos.filter(data__year=ano, data__month=mes)
    dias_eventos = set(eventos_mes.values_list('data', flat=True))

    mapa_dias_semana = {
        'segunda': 0,
        'terça': 1,
        'terca': 1,
        'quarta': 2,
        'quinta': 3,
        'sexta': 4,
        'sábado': 5,
        'sabado': 5,
        'domingo': 6,
    }

    dias_cultos = set()
    cultos = ministerio.cultos.filter(ativo=True)

    cal = calendar.Calendar(firstweekday=6)

    for culto in cultos:
        nome_dia = culto.dia.strip().lower()

        if nome_dia in mapa_dias_semana:
            weekday = mapa_dias_semana[nome_dia]

            for d in cal.itermonthdates(ano, mes):
                if d.month == mes and d.weekday() == weekday:
                    dias_cultos.add(d)

    semanas = []
    for semana in cal.monthdatescalendar(ano, mes):
        semana_info = []

        for d in semana:
            semana_info.append({
                'data': d,
                'numero': d.day,
                'mes_atual': d.month == mes,
                'tem_evento': d in dias_eventos,
                'tem_culto': d in dias_cultos,
            })

        semanas.append(semana_info)

    contexto = {
        'ministerio': ministerio,
        'eventos': eventos,
        'calendario_semanas': semanas,
        'mes_nome': nomes_meses[mes],
        'ano': ano,
    }
    return render(request, 'detalhe_ministerio.html', contexto)


# =========================
# HELPERS DO PAINEL
# =========================

def queryset_ministerios_do_usuario(user):
    return get_allowed_ministerios(user).order_by('ordem', 'nome')


def queryset_cultos_do_usuario(user):
    cultos = Culto.objects.select_related('ministerio').all()
    if user_can_manage_all(user):
        return cultos
    ministerio = ensure_user_has_ministerio(user)
    return cultos.filter(ministerio=ministerio)


def queryset_departamentos_do_usuario(user):
    departamentos = Departamento.objects.select_related('ministerio').all()
    if user_can_manage_all(user):
        return departamentos
    ministerio = ensure_user_has_ministerio(user)
    return departamentos.filter(ministerio=ministerio)


def queryset_eventos_do_usuario(user):
    eventos = Evento.objects.select_related('ministerio').all()
    if user_can_manage_all(user):
        return eventos
    ministerio = ensure_user_has_ministerio(user)
    return eventos.filter(tipo='local', ministerio=ministerio)


# =========================
# PAINEL
# =========================

@login_required
def painel_home(request):
    ministerios = queryset_ministerios_do_usuario(request.user)
    total_ministerios = ministerios.count()
    ministerios_ativos = ministerios.filter(ativo=True).count()
    ministerios_destaque = ministerios.filter(destaque=True).count()
    total_cultos = queryset_cultos_do_usuario(request.user).count()
    total_departamentos = queryset_departamentos_do_usuario(request.user).count()
    total_eventos = queryset_eventos_do_usuario(request.user).count()

    contexto = {
        'total_ministerios': total_ministerios,
        'ministerios_ativos': ministerios_ativos,
        'ministerios_destaque': ministerios_destaque,
        'total_cultos': total_cultos,
        'total_departamentos': total_departamentos,
        'total_eventos': total_eventos,
        'usuario_pode_gerenciar_tudo': user_can_manage_all(request.user),
        'ministerio_usuario': get_user_ministerio(request.user),
    }
    return render(request, 'painel/home.html', contexto)


# =========================
# CRUD MINISTÉRIOS
# =========================

@login_required
def painel_ministerios(request):
    busca = request.GET.get('busca', '').strip()
    ministerios = queryset_ministerios_do_usuario(request.user)

    if busca:
        ministerios = ministerios.filter(nome__icontains=busca)

    contexto = {
        'ministerios': ministerios,
        'busca': busca,
        'usuario_pode_gerenciar_tudo': user_can_manage_all(request.user),
    }
    return render(request, 'painel/ministerios_lista.html', contexto)


@login_required
def criar_ministerio(request):
    if not user_can_manage_all(request.user):
        messages.error(request, 'Somente o administrador geral pode cadastrar novas igrejas.')
        return redirect('painel_ministerios')

    ministerio = Ministerio()

    if request.method == 'POST':
        form = MinisterioForm(request.POST, request.FILES, instance=ministerio, user=request.user)
        cultos_formset = CultoInlineFormSet(request.POST, instance=ministerio, prefix='cultos')
        departamentos_formset = DepartamentoInlineFormSet(request.POST, instance=ministerio, prefix='departamentos')
        if form.is_valid() and cultos_formset.is_valid() and departamentos_formset.is_valid():
            ministerio = form.save()
            cultos_formset.instance = ministerio
            departamentos_formset.instance = ministerio
            cultos_formset.save()
            departamentos_formset.save()
            registrar_auditoria(
                request.user,
                RegistroAuditoria.ACAO_CRIAR,
                'Ministério',
                registro=ministerio,
                ministerio=ministerio,
                descricao=f'Criou a igreja {ministerio.nome}.',
            )
            messages.success(request, 'Igreja cadastrada com sucesso.')
            return redirect('painel_ministerios')
    else:
        form = MinisterioForm(instance=ministerio, user=request.user)
        cultos_formset = CultoInlineFormSet(instance=ministerio, prefix='cultos')
        departamentos_formset = DepartamentoInlineFormSet(instance=ministerio, prefix='departamentos')

    contexto = {
        'form': form,
        'cultos_formset': cultos_formset,
        'departamentos_formset': departamentos_formset,
        'titulo_pagina': 'Nova Igreja',
        'subtitulo_pagina': 'Cadastre uma nova congregação do Ministério Redenção.',
        'texto_botao': 'Salvar igreja',
    }
    return render(request, 'painel/ministerio_form.html', contexto)


@login_required
def editar_ministerio(request, pk):
    ministerio = get_object_or_404(queryset_ministerios_do_usuario(request.user), pk=pk)
    ensure_user_can_access_ministerio(request.user, ministerio)

    if request.method == 'POST':
        form = MinisterioForm(request.POST, request.FILES, instance=ministerio, user=request.user)
        cultos_formset = CultoInlineFormSet(request.POST, instance=ministerio, prefix='cultos')
        departamentos_formset = DepartamentoInlineFormSet(request.POST, instance=ministerio, prefix='departamentos')
        if form.is_valid() and cultos_formset.is_valid() and departamentos_formset.is_valid():
            ministerio = form.save()
            cultos_formset.save()
            departamentos_formset.save()
            registrar_auditoria(
                request.user,
                RegistroAuditoria.ACAO_EDITAR,
                'Ministério',
                registro=ministerio,
                ministerio=ministerio,
                descricao=f'Atualizou os dados da igreja {ministerio.nome}.',
            )
            messages.success(request, 'Igreja atualizada com sucesso.')
            return redirect('painel_ministerios')
    else:
        form = MinisterioForm(instance=ministerio, user=request.user)
        cultos_formset = CultoInlineFormSet(instance=ministerio, prefix='cultos')
        departamentos_formset = DepartamentoInlineFormSet(instance=ministerio, prefix='departamentos')

    contexto = {
        'form': form,
        'cultos_formset': cultos_formset,
        'departamentos_formset': departamentos_formset,
        'ministerio': ministerio,
        'titulo_pagina': 'Editar Igreja',
        'subtitulo_pagina': f'Atualize as informações de {ministerio.nome}.',
        'texto_botao': 'Salvar alterações',
    }
    return render(request, 'painel/ministerio_form.html', contexto)


@login_required
def excluir_ministerio(request, pk):
    if not user_can_manage_all(request.user):
        messages.error(request, 'Somente o administrador geral pode excluir igrejas.')
        return redirect('painel_ministerios')

    ministerio = get_object_or_404(Ministerio, pk=pk)

    if request.method == 'POST':
        nome = ministerio.nome
        registrar_auditoria(
            request.user,
            RegistroAuditoria.ACAO_EXCLUIR,
            'Ministério',
            registro=ministerio,
            ministerio=ministerio,
            descricao=f'Excluiu a igreja {nome}.',
        )
        ministerio.delete()
        messages.success(request, 'Igreja excluída com sucesso.')
        return redirect('painel_ministerios')

    contexto = {
        'ministerio': ministerio,
    }
    return render(request, 'painel/ministerio_confirmar_exclusao.html', contexto)


# =========================
# CRUD CULTOS
# =========================

@login_required
def painel_cultos(request):
    busca = request.GET.get('busca', '').strip()
    ministerio_id = request.GET.get('ministerio', '').strip()

    cultos = queryset_cultos_do_usuario(request.user).order_by('ministerio__nome', 'ordem', 'id')

    if busca:
        cultos = cultos.filter(
            Q(descricao__icontains=busca) |
            Q(dia__icontains=busca) |
            Q(horario__icontains=busca)
        )

    if ministerio_id:
        cultos = cultos.filter(ministerio_id=ministerio_id)

    ministerios = queryset_ministerios_do_usuario(request.user).order_by('nome')

    contexto = {
        'cultos': cultos,
        'ministerios': ministerios,
        'busca': busca,
        'ministerio_id': ministerio_id,
        'usuario_pode_gerenciar_tudo': user_can_manage_all(request.user),
    }
    return render(request, 'painel/cultos_lista.html', contexto)


@login_required
def criar_culto(request):
    ensure_user_has_ministerio(request.user)

    if request.method == 'POST':
        form = CultoForm(request.POST, user=request.user)
        if form.is_valid():
            culto = form.save()
            registrar_auditoria(
                request.user,
                RegistroAuditoria.ACAO_CRIAR,
                'Culto',
                registro=culto,
                ministerio=culto.ministerio,
                descricao=f'Cadastrou o culto {culto.dia} - {culto.horario} para {culto.ministerio.nome}.',
            )
            messages.success(request, 'Culto cadastrado com sucesso.')
            return redirect('painel_cultos')
    else:
        ministerio_id = request.GET.get('ministerio')
        initial = {}
        ministerios = queryset_ministerios_do_usuario(request.user)

        if ministerio_id and ministerios.filter(pk=ministerio_id).exists():
            initial['ministerio'] = ministerio_id
        elif ministerios.count() == 1:
            initial['ministerio'] = ministerios.first().pk

        form = CultoForm(initial=initial, user=request.user)

    contexto = {
        'form': form,
        'titulo_pagina': 'Novo Culto',
        'subtitulo_pagina': 'Cadastre um novo horário de culto ou reunião.',
        'texto_botao': 'Salvar culto',
    }
    return render(request, 'painel/culto_form.html', contexto)


@login_required
def editar_culto(request, pk):
    culto = get_object_or_404(queryset_cultos_do_usuario(request.user), pk=pk)

    if request.method == 'POST':
        form = CultoForm(request.POST, instance=culto, user=request.user)
        if form.is_valid():
            culto = form.save()
            registrar_auditoria(
                request.user,
                RegistroAuditoria.ACAO_EDITAR,
                'Culto',
                registro=culto,
                ministerio=culto.ministerio,
                descricao=f'Atualizou o culto {culto.dia} - {culto.horario} da igreja {culto.ministerio.nome}.',
            )
            messages.success(request, 'Culto atualizado com sucesso.')
            return redirect('painel_cultos')
    else:
        form = CultoForm(instance=culto, user=request.user)

    contexto = {
        'form': form,
        'culto': culto,
        'titulo_pagina': 'Editar Culto',
        'subtitulo_pagina': f'Atualize o horário vinculado a {culto.ministerio.nome}.',
        'texto_botao': 'Salvar alterações',
    }
    return render(request, 'painel/culto_form.html', contexto)


@login_required
def excluir_culto(request, pk):
    culto = get_object_or_404(queryset_cultos_do_usuario(request.user), pk=pk)

    if request.method == 'POST':
        registrar_auditoria(
            request.user,
            RegistroAuditoria.ACAO_EXCLUIR,
            'Culto',
            registro=culto,
            ministerio=culto.ministerio,
            descricao=f'Excluiu o culto {culto.dia} - {culto.horario} da igreja {culto.ministerio.nome}.',
        )
        culto.delete()
        messages.success(request, 'Culto excluído com sucesso.')
        return redirect('painel_cultos')

    contexto = {
        'culto': culto,
    }
    return render(request, 'painel/culto_confirmar_exclusao.html', contexto)


# =========================
# CRUD DEPARTAMENTOS
# =========================

@login_required
def painel_departamentos(request):
    busca = request.GET.get('busca', '').strip()
    ministerio_id = request.GET.get('ministerio', '').strip()

    departamentos = queryset_departamentos_do_usuario(request.user).order_by(
        'ministerio__nome', 'ordem', 'nome'
    )

    if busca:
        departamentos = departamentos.filter(nome__icontains=busca)

    if ministerio_id:
        departamentos = departamentos.filter(ministerio_id=ministerio_id)

    ministerios = queryset_ministerios_do_usuario(request.user).order_by('nome')

    contexto = {
        'departamentos': departamentos,
        'ministerios': ministerios,
        'busca': busca,
        'ministerio_id': ministerio_id,
        'usuario_pode_gerenciar_tudo': user_can_manage_all(request.user),
    }
    return render(request, 'painel/departamentos_lista.html', contexto)


@login_required
def criar_departamento(request):
    ensure_user_has_ministerio(request.user)

    if request.method == 'POST':
        form = DepartamentoForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            departamento = form.save()
            registrar_auditoria(
                request.user,
                RegistroAuditoria.ACAO_CRIAR,
                'Departamento',
                registro=departamento,
                ministerio=departamento.ministerio,
                descricao=f'Cadastrou o departamento {departamento.nome} da igreja {departamento.ministerio.nome}.',
            )
            messages.success(request, 'Departamento cadastrado com sucesso.')
            return redirect('painel_departamentos')
    else:
        ministerio_id = request.GET.get('ministerio')
        initial = {}
        ministerios = queryset_ministerios_do_usuario(request.user)

        if ministerio_id and ministerios.filter(pk=ministerio_id).exists():
            initial['ministerio'] = ministerio_id
        elif ministerios.count() == 1:
            initial['ministerio'] = ministerios.first().pk

        form = DepartamentoForm(initial=initial, user=request.user)

    contexto = {
        'form': form,
        'titulo_pagina': 'Novo Departamento',
        'subtitulo_pagina': 'Cadastre um departamento para uma igreja específica.',
        'texto_botao': 'Salvar departamento',
    }
    return render(request, 'painel/departamento_form.html', contexto)


@login_required
def editar_departamento(request, pk):
    departamento = get_object_or_404(queryset_departamentos_do_usuario(request.user), pk=pk)

    if request.method == 'POST':
        form = DepartamentoForm(request.POST, request.FILES, instance=departamento, user=request.user)
        if form.is_valid():
            departamento = form.save()
            registrar_auditoria(
                request.user,
                RegistroAuditoria.ACAO_EDITAR,
                'Departamento',
                registro=departamento,
                ministerio=departamento.ministerio,
                descricao=f'Atualizou o departamento {departamento.nome} da igreja {departamento.ministerio.nome}.',
            )
            messages.success(request, 'Departamento atualizado com sucesso.')
            return redirect('painel_departamentos')
    else:
        form = DepartamentoForm(instance=departamento, user=request.user)

    contexto = {
        'form': form,
        'departamento': departamento,
        'titulo_pagina': 'Editar Departamento',
        'subtitulo_pagina': f'Atualize as informações de {departamento.nome}.',
        'texto_botao': 'Salvar alterações',
    }
    return render(request, 'painel/departamento_form.html', contexto)


@login_required
def excluir_departamento(request, pk):
    departamento = get_object_or_404(queryset_departamentos_do_usuario(request.user), pk=pk)

    if request.method == 'POST':
        registrar_auditoria(
            request.user,
            RegistroAuditoria.ACAO_EXCLUIR,
            'Departamento',
            registro=departamento,
            ministerio=departamento.ministerio,
            descricao=f'Excluiu o departamento {departamento.nome} da igreja {departamento.ministerio.nome}.',
        )
        departamento.delete()
        messages.success(request, 'Departamento excluído com sucesso.')
        return redirect('painel_departamentos')

    contexto = {
        'departamento': departamento,
    }
    return render(request, 'painel/departamento_confirmar_exclusao.html', contexto)


# =========================
# CRUD EVENTOS
# =========================

@login_required
def painel_eventos(request):
    busca = request.GET.get('busca', '').strip()
    tipo = request.GET.get('tipo', '').strip()
    ministerio_id = request.GET.get('ministerio', '').strip()
    gratuito = request.GET.get('gratuito', '').strip()
    publico = request.GET.get('publico', '').strip()

    eventos = queryset_eventos_do_usuario(request.user).order_by('data', 'titulo')

    if busca:
        eventos = eventos.filter(titulo__icontains=busca)

    if tipo:
        eventos = eventos.filter(tipo=tipo)

    if ministerio_id:
        eventos = eventos.filter(ministerio_id=ministerio_id)

    if gratuito == '1':
        eventos = eventos.filter(gratuito=True)

    if publico:
        eventos = eventos.filter(publico=publico)

    ministerios = queryset_ministerios_do_usuario(request.user).order_by('nome')

    contexto = {
        'eventos': eventos,
        'ministerios': ministerios,
        'busca': busca,
        'tipo': tipo,
        'ministerio_id': ministerio_id,
        'gratuito': gratuito,
        'publico': publico,
        'publico_choices': Evento.PUBLICO_CHOICES,
        'usuario_pode_gerenciar_tudo': user_can_manage_all(request.user),
    }
    return render(request, 'painel/eventos_lista.html', contexto)


@login_required
def criar_evento(request):
    ensure_user_has_ministerio(request.user)

    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            evento = form.save()
            registrar_auditoria(
                request.user,
                RegistroAuditoria.ACAO_CRIAR,
                'Evento',
                registro=evento,
                ministerio=evento.ministerio,
                descricao=f'Cadastrou o evento {evento.titulo}.',
            )
            messages.success(request, 'Evento cadastrado com sucesso.')
            return redirect('painel_eventos')
    else:
        initial = {}
        ministerios = queryset_ministerios_do_usuario(request.user)
        if ministerios.count() == 1:
            initial['ministerio'] = ministerios.first().pk
        form = EventoForm(initial=initial, user=request.user)

    contexto = {
        'form': form,
        'titulo_pagina': 'Novo Evento',
        'subtitulo_pagina': 'Cadastre um evento local ou geral.',
        'texto_botao': 'Salvar evento',
        'usuario_pode_gerenciar_tudo': user_can_manage_all(request.user),
    }
    return render(request, 'painel/evento_form.html', contexto)


@login_required
def editar_evento(request, pk):
    evento = get_object_or_404(queryset_eventos_do_usuario(request.user), pk=pk)

    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES, instance=evento, user=request.user)
        if form.is_valid():
            evento = form.save()
            registrar_auditoria(
                request.user,
                RegistroAuditoria.ACAO_EDITAR,
                'Evento',
                registro=evento,
                ministerio=evento.ministerio,
                descricao=f'Atualizou o evento {evento.titulo}.',
            )
            messages.success(request, 'Evento atualizado com sucesso.')
            return redirect('painel_eventos')
    else:
        form = EventoForm(instance=evento, user=request.user)

    contexto = {
        'form': form,
        'evento': evento,
        'titulo_pagina': 'Editar Evento',
        'subtitulo_pagina': f'Atualize as informações de {evento.titulo}.',
        'texto_botao': 'Salvar alterações',
        'usuario_pode_gerenciar_tudo': user_can_manage_all(request.user),
    }
    return render(request, 'painel/evento_form.html', contexto)


@login_required
def excluir_evento(request, pk):
    evento = get_object_or_404(queryset_eventos_do_usuario(request.user), pk=pk)

    if request.method == 'POST':
        registrar_auditoria(
            request.user,
            RegistroAuditoria.ACAO_EXCLUIR,
            'Evento',
            registro=evento,
            ministerio=evento.ministerio,
            descricao=f'Excluiu o evento {evento.titulo}.',
        )
        evento.delete()
        messages.success(request, 'Evento excluído com sucesso.')
        return redirect('painel_eventos')

    contexto = {
        'evento': evento,
    }
    return render(request, 'painel/evento_confirmar_exclusao.html', contexto)
