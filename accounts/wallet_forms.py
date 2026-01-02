from django import forms
from .models import WalletTransaction, GoalAllocation


class WalletTransactionForm(forms.ModelForm):
    """
    Formulaire pour ajouter une transaction (entrée ou sortie d'argent).
    """
    class Meta:
        model = WalletTransaction
        fields = ('transaction_type', 'amount', 'category', 'description', 'date')
        widgets = {
            'transaction_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Montant en FCFA',
                'step': '0.01',
                'min': '0.01'
            }),
            'category': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Salaire, Freelance, Courses...'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Description de la transaction'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            from django.utils import timezone
            self.initial['date'] = timezone.now().date()


class GoalAllocationForm(forms.ModelForm):
    """
    Formulaire pour allouer des fonds à un objectif d'épargne.
    """
    class Meta:
        model = GoalAllocation
        fields = ('amount',)
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Montant à allouer',
                'step': '0.01',
                'min': '0.01'
            })
        }
