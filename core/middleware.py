from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

from .access import user_can_manage_all


class AdminAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        admin_prefix = reverse('admin:index')
        login_url = reverse('login')

        if request.path.startswith(admin_prefix):
            if request.user.is_authenticated and not user_can_manage_all(request.user):
                messages.error(
                    request,
                    'O Django Admin é liberado somente para o administrador geral. Use o painel da sua igreja para trabalhar.'
                )
                return redirect('painel_home')

            if not request.user.is_authenticated and request.path == admin_prefix:
                return redirect(f'{login_url}?next={request.path}')

        return self.get_response(request)
