from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Culto, Evento, Ministerio, PerfilAcesso, RegistroAuditoria


class PainelAcessoPorIgrejaTests(TestCase):
    def setUp(self):
        self.igreja_1 = Ministerio.objects.create(nome='Igreja 1', slug='igreja-1')
        self.igreja_2 = Ministerio.objects.create(nome='Igreja 2', slug='igreja-2')

        self.admin_geral = User.objects.create_user(username='admin', password='123456')
        PerfilAcesso.objects.filter(user=self.admin_geral).update(
            escopo=PerfilAcesso.ESCOPO_ADMIN_GERAL,
            ministerio=None,
        )

        self.usuario_igreja_1 = User.objects.create_user(username='igreja1', password='123456')
        PerfilAcesso.objects.filter(user=self.usuario_igreja_1).update(
            escopo=PerfilAcesso.ESCOPO_ADMIN_IGREJA,
            ministerio=self.igreja_1,
        )

        self.culto_igreja_1 = Culto.objects.create(
            ministerio=self.igreja_1,
            dia='Domingo',
            horario='19:00',
        )
        self.culto_igreja_2 = Culto.objects.create(
            ministerio=self.igreja_2,
            dia='Quarta',
            horario='20:00',
        )

        self.evento_igreja_1 = Evento.objects.create(
            titulo='Evento local 1',
            slug='evento-local-1',
            tipo='local',
            ministerio=self.igreja_1,
            data=date(2026, 3, 20),
        )
        self.evento_geral = Evento.objects.create(
            titulo='Evento geral',
            slug='evento-geral',
            tipo='geral',
            data=date(2026, 3, 22),
        )

    def test_usuario_comum_ve_apenas_sua_igreja(self):
        self.client.login(username='igreja1', password='123456')

        response = self.client.get(reverse('painel_ministerios'))

        self.assertContains(response, 'Igreja 1')
        self.assertNotContains(response, 'Igreja 2')

    def test_usuario_comum_ve_apenas_cultos_da_propria_igreja(self):
        self.client.login(username='igreja1', password='123456')

        response = self.client.get(reverse('painel_cultos'))

        self.assertContains(response, '19:00')
        self.assertNotContains(response, '20:00')

    def test_usuario_comum_nao_pode_criar_evento_geral(self):
        self.client.login(username='igreja1', password='123456')

        response = self.client.post(reverse('criar_evento'), {
            'titulo': 'Novo geral',
            'slug': 'novo-geral',
            'tipo': 'geral',
            'data': '2026-03-25',
            'ativo': 'on',
            'destaque': '',
        })

        self.assertContains(response, 'Somente o administrador geral pode criar eventos gerais.')
        self.assertFalse(Evento.objects.filter(slug='novo-geral').exists())

    def test_admin_geral_consegue_ver_todas_as_igrejas(self):
        self.client.login(username='admin', password='123456')

        response = self.client.get(reverse('painel_ministerios'))

        self.assertContains(response, 'Igreja 1')
        self.assertContains(response, 'Igreja 2')

    def test_usuario_comum_e_redirecionado_ao_tentar_abrir_admin(self):
        self.client.login(username='igreja1', password='123456')

        response = self.client.get('/admin/', follow=True)

        self.assertRedirects(response, reverse('painel_home'))
        self.assertContains(response, 'O Django Admin é liberado somente para o administrador geral.')

    def test_auditoria_e_registrada_ao_criar_culto(self):
        self.client.login(username='igreja1', password='123456')

        response = self.client.post(reverse('criar_culto'), {
            'ministerio': self.igreja_1.pk,
            'dia': 'Sexta',
            'horario': '19:30',
            'descricao': 'Culto de oração',
            'ordem': 0,
            'ativo': 'on',
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            RegistroAuditoria.objects.filter(
                user=self.usuario_igreja_1,
                acao=RegistroAuditoria.ACAO_CRIAR,
                entidade='Culto',
                ministerio=self.igreja_1,
            ).exists()
        )
