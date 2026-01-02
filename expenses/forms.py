from django import forms
from .models import Expense, Category


class ExpenseForm(forms.ModelForm):
    """
    Formulaire de création et modification de dépenses.
    """
    class Meta:
        model = Expense
        fields = ('category', 'amount', 'description', 'notes', 'date')
        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Montant en FCFA',
                'step': '0.01',
                'min': '0.01'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Achat de provisions'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notes supplémentaires (optionnel)'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Définir la date d'aujourd'hui par défaut si c'est un nouveau formulaire
        if not self.instance.pk:
            from django.utils import timezone
            self.initial['date'] = timezone.now().date()


class CategoryForm(forms.ModelForm):
    """
    Formulaire de création et modification de catégories.
    """
    class Meta:
        model = Category
        fields = ('name', 'description', 'icon', 'color')
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Alimentation'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description de la catégorie (optionnel)'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: bi-cart, bi-bus-front'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            })
        }
