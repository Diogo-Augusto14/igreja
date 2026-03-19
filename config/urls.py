from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from core.views import (
    criar_culto,
    criar_departamento,
    criar_ministerio,
    detalhe_ministerio,
    editar_culto,
    editar_departamento,
    editar_ministerio,
    excluir_culto,
    excluir_departamento,
    excluir_ministerio,
    home,
    ministerio,
    painel_cultos,
    painel_departamentos,
    painel_home,
    painel_ministerios,
    criar_evento,
    editar_evento,
    excluir_evento,
    painel_eventos,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', home, name='home'),
    path('ministerio/', ministerio, name='ministerio'),
    path('ministerio/<slug:slug>/', detalhe_ministerio, name='detalhe_ministerio'),

    path('painel/', painel_home, name='painel_home'),

    path('painel/ministerios/', painel_ministerios, name='painel_ministerios'),
    path('painel/ministerios/novo/', criar_ministerio, name='criar_ministerio'),
    path('painel/ministerios/<int:pk>/editar/', editar_ministerio, name='editar_ministerio'),
    path('painel/ministerios/<int:pk>/excluir/', excluir_ministerio, name='excluir_ministerio'),

    path('painel/cultos/', painel_cultos, name='painel_cultos'),
    path('painel/cultos/novo/', criar_culto, name='criar_culto'),
    path('painel/cultos/<int:pk>/editar/', editar_culto, name='editar_culto'),
    path('painel/cultos/<int:pk>/excluir/', excluir_culto, name='excluir_culto'),

    path('painel/departamentos/', painel_departamentos, name='painel_departamentos'),
    path('painel/departamentos/novo/', criar_departamento, name='criar_departamento'),
    path('painel/departamentos/<int:pk>/editar/', editar_departamento, name='editar_departamento'),
    path('painel/departamentos/<int:pk>/excluir/', excluir_departamento, name='excluir_departamento'),

    path('painel/eventos/', painel_eventos, name='painel_eventos'),
    path('painel/eventos/novo/', criar_evento, name='criar_evento'),
    path('painel/eventos/<int:pk>/editar/', editar_evento, name='editar_evento'),
    path('painel/eventos/<int:pk>/excluir/', excluir_evento, name='excluir_evento'),

    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)