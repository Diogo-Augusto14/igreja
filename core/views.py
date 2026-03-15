from django.shortcuts import render

def home(request):
    
    return render(request, 'home.html', {})
def ministerio(request):
    return render(request, 'ministerio.html', {})
def detalhe_ministerio(request):
    return render(request, 'detalhe-ministerio', {})
