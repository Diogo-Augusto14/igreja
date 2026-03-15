from django import forms
from .models import Ministerio


class MinisterioForm(forms.ModelForm):
    class Meta:
        model = Ministerio
        fields = [
            'nome',
            'slug',
            'subtitulo',
            'resumo',
            'descricao',
            'lider',
            'cargo_lider',
            'local',
            'dia_reuniao',
            'horario',
            'contato',
            'versiculo',
            'imagem_capa',
            'imagem_principal',
            'ativo',
            'destaque',
            'ordem',
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Redenção Sagrada Família'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: redencao-sagrada-familia'}),
            'subtitulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Uma igreja para toda a família'}),
            'resumo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Resumo curto para aparecer no card'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Descrição completa do ministério'}),
            'lider': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do líder'}),
            'cargo_lider': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Pastor dirigente'}),
            'local': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Endereço ou bairro'}),
            'dia_reuniao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Quarta e Domingo'}),
            'horario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 19:30'}),
            'contato': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefone ou WhatsApp'}),
            'versiculo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: João 3:16'}),
            'imagem_capa': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'imagem_principal': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'destaque': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ordem': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
        }

    def clean_slug(self):
        slug = self.cleaned_data['slug']
        qs = Ministerio.objects.filter(slug=slug)

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError('Já existe um ministério com esse slug.')

        return slug