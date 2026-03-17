from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CultoForm, DepartamentoForm, MinisterioForm
from .models import Culto, Departamento, Ministerio


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
        Ministerio.objects.prefetch_related('cultos', 'departamentos'),
        slug=slug,
        ativo=True
    )

    contexto = {
        'ministerio': ministerio,
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
        cultos = cultos.filter(descricao__icontains=busca) | cultos.filter(dia__icontains=busca)

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