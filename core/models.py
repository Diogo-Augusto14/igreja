from django.db import models
from django.utils.text import slugify


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