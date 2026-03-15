from django.shortcuts import get_object_or_404, render
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