from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from core.views import (
    home,
    ministerio,
    detalhe_ministerio,
    painel_home,
    painel_ministerios,
    criar_ministerio,
    editar_ministerio,
    excluir_ministerio,
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
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)