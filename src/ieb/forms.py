from django import forms
from .models import AtividadeRegistro, Meta, Indicador, Projeto, Subatividade

class AtividadeRegistroForm(forms.ModelForm):
    indicadores = forms.ModelMultipleChoiceField(
        queryset=Indicador.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    # Adicionando o campo de e-mail da organização
    email_organizacao = forms.EmailField(
        label='E-mail da Organização',
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Digite o e-mail da organização'})
    )

    class Meta:
        model = AtividadeRegistro
        fields = [
            'projeto', 'componente', 'atividade', 'subatividade', 'equipe_projeto',
            'data_inicio', 'data_final', 'desafios', 'propostas',
            'sucesso', 'melhores_praticas', 'equipe_adicional',
            'descricao', 'local', 'comentarios',
            'email_organizacao'
        ]
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'data_final': forms.DateInput(attrs={'type': 'date'}),
            'equipe_adicional': forms.CheckboxSelectMultiple,
            'desafios': forms.Textarea(attrs={'maxlength': 255}),
            'propostas': forms.Textarea(attrs={'maxlength': 255}),
            'sucesso': forms.Textarea(attrs={'maxlength': 255}),
            'melhores_praticas': forms.Textarea(attrs={'maxlength': 255}),
            'descricao': forms.Textarea(),
            'comentarios': forms.Textarea(attrs={'maxlength': 255}),
            'local': forms.Textarea(attrs={'maxlength': 255}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['projeto'].required = True
        self.fields['projeto'].queryset = Projeto.objects.all()  # Certifique-se de que há Projetos no banco de dados
        self.fields['projeto'].widget = forms.Select()
        self.fields['componente'].required = True
        self.fields['atividade'].required = True
        self.fields['subatividade'].required = False
        if 'atividade' in self.data:
            try:
                atividade_id = int(self.data.get('atividade'))
                self.fields['subatividade'].queryset = Subatividade.objects.filter(atividade_id=atividade_id)
            except (ValueError, TypeError):
                self.fields['subatividade'].queryset = Subatividade.objects.none()
        elif self.instance.pk and self.instance.atividade_id:
            self.fields['subatividade'].queryset = Subatividade.objects.filter(atividade_id=self.instance.atividade_id)
        else:
            self.fields['subatividade'].queryset = Subatividade.objects.none()
        self.fields['equipe_projeto'].required = True
        self.fields['data_inicio'].required = True
        self.fields['data_final'].required = True
        self.fields['descricao'].required = True
        self.fields['local'].required = True

        self.fields['descricao'].widget.attrs.update({
        'placeholder': 'Descreva a atividade realizada'
    })
        self.fields['local'].widget.attrs.update({
        'placeholder': 'Indique o local em que a atividade foi realizada. Aldeia - Terra Indígena'
    })
        self.fields['comentarios'].widget.attrs.update({
        'placeholder': 'Comente algo relevante sobre a realização da atividade'
    })
        self.fields['desafios'].widget.attrs.update({
        'placeholder': 'Algum desafio encontrado? Comente aqui...'
    })
        self.fields['propostas'].widget.attrs.update({
        'placeholder': 'Alguma proposta a sugerir? Comente aqui...'
    })
        self.fields['sucesso'].widget.attrs.update({
        'placeholder': 'História de sucesso a compartilhar? Comente aqui...'
    })
        self.fields['melhores_praticas'].widget.attrs.update({
        'placeholder': 'Alguma boa prática a compartilhar? Comente aqui...'
    })

  
  
        if 'atividade' in self.data:
            try:
                atividade_id = int(self.data.get('atividade'))
                self.fields['indicadores'].queryset = Indicador.objects.filter(meta__atividade_id=atividade_id).distinct()
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['indicadores'].queryset = self.instance.atividade.meta_set.all()

    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_final = cleaned_data.get('data_final')

        if data_inicio and data_final:
            if data_inicio > data_final:
                self.add_error('data_final', 'A data final não pode ser anterior à data de início.')

        return cleaned_data
