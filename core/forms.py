from django import forms
from .models import Culto, Departamento, Ministerio


class MinisterioForm(forms.ModelForm):
    class Meta:
        model = Ministerio
        fields = [
            'nome',
            'slug',
            'subtitulo',
            'resumo',
            'descricao',
            'pastor_nome',
            'pastora_nome',
            'foto_casal_lideranca',
            'local',
            'contato',
            'versiculo',
            'imagem_capa',
            'imagem_principal',
            'ativo',
            'destaque',
            'ordem',
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Ministério Redenção Sagrada Família'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: ministerio-redencao-sagrada-familia'}),
            'subtitulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Uma igreja para toda a família'}),
            'resumo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Resumo curto para o card'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Descrição completa da congregação'}),
            'pastor_nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do pastor'}),
            'pastora_nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da pastora'}),
            'foto_casal_lideranca': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'local': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Bairro Sagrada Família - Divinópolis/MG'}),
            'contato': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefone / WhatsApp'}),
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
            raise forms.ValidationError('Já existe uma igreja com esse slug.')

        return slug


class CultoForm(forms.ModelForm):
    class Meta:
        model = Culto
        fields = [
            'ministerio',
            'dia',
            'horario',
            'descricao',
            'ordem',
            'ativo',
        ]
        widgets = {
            'ministerio': forms.Select(attrs={'class': 'form-control'}),
            'dia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Domingo'}),
            'horario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 18:00 Oração / 19:00 Culto'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Culto principal da semana'}),
            'ordem': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class DepartamentoForm(forms.ModelForm):
    class Meta:
        model = Departamento
        fields = [
            'ministerio',
            'nome',
            'descricao',
            'imagem',
            'lider_nome',
            'lider_nome_esposa',
            'foto_lideranca',
            'ordem',
            'ativo',
        ]
        widgets = {
            'ministerio': forms.Select(attrs={'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Ministério Infantil'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Descreva a função desse departamento'}),
            'imagem': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'lider_nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do líder'}),
            'lider_nome_esposa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da líder'}),
            'foto_lideranca': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'ordem': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }