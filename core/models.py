from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify

User = get_user_model()


class Ministerio(models.Model):
    nome = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, blank=True)
    subtitulo = models.CharField(max_length=200, blank=True)
    resumo = models.CharField(max_length=300, blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)

    pastor_nome = models.CharField(max_length=120, blank=True, null=True)
    pastora_nome = models.CharField(max_length=120, blank=True, null=True)

    foto_casal_lideranca = models.ImageField(
        upload_to='ministerios/lideranca/',
        blank=True,
        null=True
    )

    local = models.CharField(max_length=200, blank=True, null=True)
    contato = models.CharField(max_length=50, blank=True)
    versiculo = models.CharField(max_length=255, blank=True)

    imagem_capa = models.ImageField(
        upload_to='ministerios/capas/',
        blank=True,
        null=True
    )

    imagem_principal = models.ImageField(
        upload_to='ministerios/principais/',
        blank=True,
        null=True
    )

    ativo = models.BooleanField(default=True)
    destaque = models.BooleanField(default=False)
    ordem = models.PositiveIntegerField(default=0)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['ordem', 'nome']
        verbose_name = 'Ministério'
        verbose_name_plural = 'Ministérios'

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if not self.slug:
            slug_base = slugify(self.nome)
            slug = slug_base
            contador = 1

            while Ministerio.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{slug_base}-{contador}'
                contador += 1

            self.slug = slug

        super().save(*args, **kwargs)


class PerfilAcesso(models.Model):
    ESCOPO_ADMIN_GERAL = 'admin_geral'
    ESCOPO_ADMIN_IGREJA = 'admin_igreja'
    ESCOPO_CHOICES = [
        (ESCOPO_ADMIN_GERAL, 'Administrador geral'),
        (ESCOPO_ADMIN_IGREJA, 'Administrador da igreja'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil_acesso'
    )
    ministerio = models.ForeignKey(
        Ministerio,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='usuarios_vinculados'
    )
    escopo = models.CharField(
        max_length=20,
        choices=ESCOPO_CHOICES,
        default=ESCOPO_ADMIN_IGREJA,
    )
    observacoes = models.CharField(max_length=255, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Perfil de acesso'
        verbose_name_plural = 'Perfis de acesso'

    def __str__(self):
        if self.escopo == self.ESCOPO_ADMIN_GERAL:
            return f'{self.user.username} - Administrador geral'
        return f'{self.user.username} - {self.ministerio or "Sem igreja"}'

    def clean(self):
        if self.escopo == self.ESCOPO_ADMIN_GERAL:
            self.ministerio = None

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

        user = self.user
        deve_acessar_admin = user.is_superuser or self.escopo == self.ESCOPO_ADMIN_GERAL
        if user.is_staff != deve_acessar_admin:
            user.is_staff = deve_acessar_admin
            user.save(update_fields=['is_staff'])


class Culto(models.Model):
    ministerio = models.ForeignKey(
        Ministerio,
        on_delete=models.CASCADE,
        related_name='cultos'
    )
    dia = models.CharField(max_length=50)
    horario = models.CharField(max_length=50)
    descricao = models.CharField(max_length=200, blank=True)
    ordem = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['ordem', 'id']
        verbose_name = 'Culto'
        verbose_name_plural = 'Cultos'

    def __str__(self):
        return f'{self.ministerio.nome} - {self.dia} - {self.horario}'


class Departamento(models.Model):
    ministerio = models.ForeignKey(
        Ministerio,
        on_delete=models.CASCADE,
        related_name='departamentos'
    )

    nome = models.CharField(max_length=150)
    descricao = models.TextField(blank=True, null=True)

    imagem = models.ImageField(
        upload_to='departamentos/',
        blank=True,
        null=True
    )

    lider_nome = models.CharField(
        max_length=120,
        blank=True,
        null=True
    )

    lider_nome_esposa = models.CharField(
        max_length=120,
        blank=True,
        null=True
    )

    foto_lideranca = models.ImageField(
        upload_to='departamentos/lideranca/',
        blank=True,
        null=True
    )

    ordem = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['ordem', 'nome']
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'

    def __str__(self):
        return f'{self.ministerio.nome} - {self.nome}'


class Evento(models.Model):
    TIPO_CHOICES = [
        ('local', 'Evento da igreja'),
        ('geral', 'Evento geral'),
    ]

    ministerio = models.ForeignKey(
        'Ministerio',
        on_delete=models.CASCADE,
        related_name='eventos',
        blank=True,
        null=True
    )

    titulo = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, blank=True)
    descricao = models.TextField(blank=True, null=True)

    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES,
        default='local'
    )

    data = models.DateField()
    horario = models.CharField(max_length=50, blank=True, null=True)
    local = models.CharField(max_length=200, blank=True, null=True)

    imagem = models.ImageField(
        upload_to='eventos/',
        blank=True,
        null=True
    )

    ativo = models.BooleanField(default=True)
    destaque = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['data', 'titulo']
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'

    def __str__(self):
        if self.tipo == 'geral':
            return f'{self.titulo} (Geral)'
        return f'{self.titulo} - {self.ministerio.nome if self.ministerio else "Sem igreja"}'

    def save(self, *args, **kwargs):
        if not self.slug:
            slug_base = slugify(self.titulo)
            slug = slug_base
            contador = 1

            while Evento.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{slug_base}-{contador}'
                contador += 1

            self.slug = slug

        if self.tipo == 'geral':
            self.ministerio = None

        super().save(*args, **kwargs)


class RegistroAuditoria(models.Model):
    ACAO_CRIAR = 'criar'
    ACAO_EDITAR = 'editar'
    ACAO_EXCLUIR = 'excluir'
    ACAO_LOGIN = 'login'
    ACAO_CHOICES = [
        (ACAO_CRIAR, 'Criou'),
        (ACAO_EDITAR, 'Editou'),
        (ACAO_EXCLUIR, 'Excluiu'),
        (ACAO_LOGIN, 'Entrou no sistema'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='registros_auditoria'
    )
    ministerio = models.ForeignKey(
        Ministerio,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='registros_auditoria'
    )
    acao = models.CharField(max_length=20, choices=ACAO_CHOICES)
    entidade = models.CharField(max_length=80)
    registro_id = models.PositiveIntegerField(blank=True, null=True)
    descricao = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Registro de auditoria'
        verbose_name_plural = 'Registros de auditoria'

    def __str__(self):
        usuario = self.user.username if self.user else 'Sistema'
        return f'{usuario} - {self.get_acao_display()} {self.entidade}'
