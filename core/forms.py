from django import forms

from .access import get_allowed_ministerios, user_can_manage_all
from .models import Culto, Departamento, Evento, Ministerio


class MinisterioForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

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


class BasePainelMinisterioForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        if 'ministerio' in self.fields:
            self.fields['ministerio'].queryset = get_allowed_ministerios(user).order_by('nome')


class CultoForm(BasePainelMinisterioForm):
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


class DepartamentoForm(BasePainelMinisterioForm):
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


class EventoForm(BasePainelMinisterioForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, user=user, **kwargs)
        if not user_can_manage_all(user):
            self.fields['tipo'].choices = [choice for choice in self.fields['tipo'].choices if choice[0] == 'local']
            self.fields['tipo'].initial = 'local'

    class Meta:
        model = Evento
        fields = [
            'titulo',
            'slug',
            'descricao',
            'tipo',
            'ministerio',
            'data',
            'horario',
            'local',
            'imagem',
            'ativo',
            'destaque',
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 12 horas de adoração'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 12-horas-de-adoracao'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Descrição do evento'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'ministerio': forms.Select(attrs={'class': 'form-control'}),
            'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'horario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 19:00'}),
            'local': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Sede - Divinópolis/MG'}),
            'imagem': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'destaque': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        ministerio = cleaned_data.get('ministerio')

        if tipo == 'local' and not ministerio:
            self.add_error('ministerio', 'Selecione uma igreja para evento local.')

        if tipo == 'geral' and not user_can_manage_all(self.user):
            self.add_error('tipo', 'Somente o administrador geral pode criar eventos gerais.')

        if tipo == 'geral':
            cleaned_data['ministerio'] = None

        return cleaned_data
