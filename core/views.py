from datetime import date
import calendar

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CultoForm, DepartamentoForm, EventoForm, MinisterioForm
from .models import Culto, Departamento, Evento, Ministerio


def home(request):
    return render(request, 'home.html', {})


def ministerio(request):
    ministerios = Ministerio.objects.filter(ativo=True).order_by('ordem', 'nome')

    contexto = {
        'ministerios': ministerios,
    }
    return render(request, 'ministerio.html', contexto)


def detalhe_ministerio(request, slug):
    ministerio = get_object_or_404(
        Ministerio.objects.prefetch_related('cultos', 'departamentos', 'eventos'),
        slug=slug,
        ativo=True
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

    eventos = Evento.objects.filter(
        ativo=True
    ).filter(
        Q(tipo='geral') |
        Q(tipo='local', ministerio=ministerio)
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


@login_required
def painel_home(request):
    total_ministerios = Ministerio.objects.count()
    ministerios_ativos = Ministerio.objects.filter(ativo=True).count()
    ministerios_destaque = Ministerio.objects.filter(destaque=True).count()

    contexto = {
        'total_ministerios': total_ministerios,
        'ministerios_ativos': ministerios_ativos,
        'ministerios_destaque': ministerios_destaque,
    }
    return render(request, 'painel/home.html', contexto)


# =========================
# CRUD MINISTÉRIOS
# =========================

@login_required
def painel_ministerios(request):
    busca = request.GET.get('busca', '').strip()

    ministerios = Ministerio.objects.all().order_by('ordem', 'nome')

    if busca:
        ministerios = ministerios.filter(nome__icontains=busca)

    contexto = {
        'ministerios': ministerios,
        'busca': busca,
    }
    return render(request, 'painel/ministerios_lista.html', contexto)


@login_required
def criar_ministerio(request):
    if request.method == 'POST':
        form = MinisterioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('painel_ministerios')
    else:
        form = MinisterioForm()

    contexto = {
        'form': form,
        'titulo_pagina': 'Nova Igreja',
        'subtitulo_pagina': 'Cadastre uma nova congregação do Ministério Redenção.',
        'texto_botao': 'Salvar igreja',
    }
    return render(request, 'painel/ministerio_form.html', contexto)


@login_required
def editar_ministerio(request, pk):
    ministerio = get_object_or_404(Ministerio, pk=pk)

    if request.method == 'POST':
        form = MinisterioForm(request.POST, request.FILES, instance=ministerio)
        if form.is_valid():
            form.save()
            return redirect('painel_ministerios')
    else:
        form = MinisterioForm(instance=ministerio)

    contexto = {
        'form': form,
        'ministerio': ministerio,
        'titulo_pagina': 'Editar Igreja',
        'subtitulo_pagina': f'Atualize as informações de {ministerio.nome}.',
        'texto_botao': 'Salvar alterações',
    }
    return render(request, 'painel/ministerio_form.html', contexto)


@login_required
def excluir_ministerio(request, pk):
    ministerio = get_object_or_404(Ministerio, pk=pk)

    if request.method == 'POST':
        ministerio.delete()
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

    cultos = Culto.objects.select_related('ministerio').all().order_by(
        'ministerio__nome', 'ordem', 'id'
    )

    if busca:
        cultos = cultos.filter(
            Q(descricao__icontains=busca) |
            Q(dia__icontains=busca) |
            Q(horario__icontains=busca)
        )

    if ministerio_id:
        cultos = cultos.filter(ministerio_id=ministerio_id)

    ministerios = Ministerio.objects.all().order_by('nome')

    contexto = {
        'cultos': cultos,
        'ministerios': ministerios,
        'busca': busca,
        'ministerio_id': ministerio_id,
    }
    return render(request, 'painel/cultos_lista.html', contexto)


@login_required
def criar_culto(request):
    if request.method == 'POST':
        form = CultoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('painel_cultos')
    else:
        ministerio_id = request.GET.get('ministerio')
        initial = {}

        if ministerio_id:
            initial['ministerio'] = ministerio_id

        form = CultoForm(initial=initial)

    contexto = {
        'form': form,
        'titulo_pagina': 'Novo Culto',
        'subtitulo_pagina': 'Cadastre um novo horário de culto ou reunião.',
        'texto_botao': 'Salvar culto',
    }
    return render(request, 'painel/culto_form.html', contexto)


@login_required
def editar_culto(request, pk):
    culto = get_object_or_404(Culto, pk=pk)

    if request.method == 'POST':
        form = CultoForm(request.POST, instance=culto)
        if form.is_valid():
            form.save()
            return redirect('painel_cultos')
    else:
        form = CultoForm(instance=culto)

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
    culto = get_object_or_404(Culto, pk=pk)

    if request.method == 'POST':
        culto.delete()
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

    departamentos = Departamento.objects.select_related('ministerio').all().order_by(
        'ministerio__nome', 'ordem', 'nome'
    )

    if busca:
        departamentos = departamentos.filter(nome__icontains=busca)

    if ministerio_id:
        departamentos = departamentos.filter(ministerio_id=ministerio_id)

    ministerios = Ministerio.objects.all().order_by('nome')

    contexto = {
        'departamentos': departamentos,
        'ministerios': ministerios,
        'busca': busca,
        'ministerio_id': ministerio_id,
    }
    return render(request, 'painel/departamentos_lista.html', contexto)


@login_required
def criar_departamento(request):
    if request.method == 'POST':
        form = DepartamentoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('painel_departamentos')
    else:
        ministerio_id = request.GET.get('ministerio')
        initial = {}

        if ministerio_id:
            initial['ministerio'] = ministerio_id

        form = DepartamentoForm(initial=initial)

    contexto = {
        'form': form,
        'titulo_pagina': 'Novo Departamento',
        'subtitulo_pagina': 'Cadastre um departamento para uma igreja específica.',
        'texto_botao': 'Salvar departamento',
    }
    return render(request, 'painel/departamento_form.html', contexto)


@login_required
def editar_departamento(request, pk):
    departamento = get_object_or_404(Departamento, pk=pk)

    if request.method == 'POST':
        form = DepartamentoForm(request.POST, request.FILES, instance=departamento)
        if form.is_valid():
            form.save()
            return redirect('painel_departamentos')
    else:
        form = DepartamentoForm(instance=departamento)

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
    departamento = get_object_or_404(Departamento, pk=pk)

    if request.method == 'POST':
        departamento.delete()
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

    eventos = Evento.objects.select_related('ministerio').all().order_by('data', 'titulo')

    if busca:
        eventos = eventos.filter(titulo__icontains=busca)

    if tipo:
        eventos = eventos.filter(tipo=tipo)

    if ministerio_id:
        eventos = eventos.filter(ministerio_id=ministerio_id)

    ministerios = Ministerio.objects.all().order_by('nome')

    contexto = {
        'eventos': eventos,
        'ministerios': ministerios,
        'busca': busca,
        'tipo': tipo,
        'ministerio_id': ministerio_id,
    }
    return render(request, 'painel/eventos_lista.html', contexto)


@login_required
def criar_evento(request):
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('painel_eventos')
    else:
        form = EventoForm()

    contexto = {
        'form': form,
        'titulo_pagina': 'Novo Evento',
        'subtitulo_pagina': 'Cadastre um evento local ou geral.',
        'texto_botao': 'Salvar evento',
    }
    return render(request, 'painel/evento_form.html', contexto)


@login_required
def editar_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk)

    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES, instance=evento)
        if form.is_valid():
            form.save()
            return redirect('painel_eventos')
    else:
        form = EventoForm(instance=evento)

    contexto = {
        'form': form,
        'evento': evento,
        'titulo_pagina': 'Editar Evento',
        'subtitulo_pagina': f'Atualize as informações de {evento.titulo}.',
        'texto_botao': 'Salvar alterações',
    }
    return render(request, 'painel/evento_form.html', contexto)


@login_required
def excluir_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk)

    if request.method == 'POST':
        evento.delete()
        return redirect('painel_eventos')

    contexto = {
        'evento': evento,
    }
    return render(request, 'painel/evento_confirmar_exclusao.html', contexto)