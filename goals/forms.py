from django import forms
from .models import Goal, Contribution


class GoalForm(forms.ModelForm):
    """
    Formulaire de création et modification d'objectifs financiers.
    """
    class Meta:
        model = Goal
        fields = ('title', 'description', 'target_amount', 'deadline', 'status')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Achat d\'une voiture'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Décrivez votre objectif...'
            }),
            'target_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Montant cible en FCFA',
                'step': '0.01',
                'min': '0.01'
            }),
            'deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pour un nouvel objectif, ne pas afficher le champ status
        if not self.instance.pk:
            self.fields.pop('status')


class ContributionForm(forms.ModelForm):
    """
    Formulaire d'ajout de contribution à un objectif.
    """
    class Meta:
        model = Contribution
        fields = ('amount', 'note', 'date')
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Montant à ajouter',
                'step': '0.01',
                'min': '0.01'
            }),
            'note': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Note (optionnel)'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Définir la date d'aujourd'hui par défaut
        if not self.instance.pk:
            from django.utils import timezone
            self.initial['date'] = timezone.now().date()
