from django.contrib import admin
from django.urls import path
from core.views import home, ministerio, detalhe_ministerio

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('ministerio/', ministerio, name='ministerio'),
    path('ministerio/<slug:slug>/', detalhe_ministerio, name='detalhe_ministerio'),
]