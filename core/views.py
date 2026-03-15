from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import MinisterioForm
from .models import Ministerio


def home(request):
    return render(request, 'home.html', {})


def ministerio(request):
    ministerios = Ministerio.objects.filter(ativo=True).order_by('ordem', 'nome')

    contexto = {
        'ministerios': ministerios,
    }
    return render(request, 'ministerio.html', contexto)


def detalhe_ministerio(request, slug):
    ministerio = get_object_or_404(Ministerio, slug=slug, ativo=True)

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
        'titulo_pagina': 'Novo Ministério',
        'subtitulo_pagina': 'Cadastre uma nova congregação do Ministério Redenção.',
        'texto_botao': 'Salvar ministério',
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
        'titulo_pagina': 'Editar Ministério',
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