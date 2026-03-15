from django.db import models
from django.utils.text import slugify


class Ministerio(models.Model):
    nome = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, blank=True)
    subtitulo = models.CharField(max_length=200, blank=True)
    resumo = models.CharField(max_length=300)
    descricao = models.TextField()
    lider = models.CharField(max_length=120)
    cargo_lider = models.CharField(max_length=120, blank=True)
    local = models.CharField(max_length=200)
    dia_reuniao = models.CharField(max_length=100, blank=True)
    horario = models.CharField(max_length=100, blank=True)
    contato = models.CharField(max_length=50, blank=True)
    versiculo = models.CharField(max_length=255, blank=True)
    imagem_capa = models.ImageField(upload_to='ministerios/capas/')
    imagem_principal = models.ImageField(upload_to='ministerios/principais/')
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