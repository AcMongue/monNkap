from django import forms
from .models import WalletTransaction, GoalAllocation
from expenses.models import Category


class WalletTransactionForm(forms.ModelForm):
    """
    Formulaire pour ajouter une transaction (entrée ou sortie d'argent).
    """
    # Champ catégorie personnalisé pour saisie libre
    category_name = forms.CharField(
        max_length=100,
        required=False,
        label='Catégorie',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: Salaire, Freelance, Courses...',
            'list': 'category-suggestions'
        })
    )
    
    class Meta:
        model = WalletTransaction
        # Exclure 'category' et 'wallet' car gérés manuellement
        exclude = ('category', 'wallet', 'expense')
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
        else:
            # Si on édite, pré-remplir le nom de la catégorie
            if self.instance.category:
                self.initial['category_name'] = self.instance.category.name
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Créer ou récupérer la catégorie avec normalisation robuste
        category_name = self.cleaned_data.get('category_name')
        if category_name:
            # Normalisation : trim, title case, suppression espaces multiples
            normalized_name = ' '.join(category_name.strip().split()).title()
            
            # Recherche insensible à la casse pour éviter les doublons
            category = Category.objects.filter(name__iexact=normalized_name).first()
            
            if not category:
                # Créer la catégorie si elle n'existe pas
                category = Category.objects.create(
                    name=normalized_name,
                    icon='bi-wallet2',
                    color='#0066FF'
                )
            
            instance.category = category
        
        if commit:
            instance.save()
        
        return instance


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
