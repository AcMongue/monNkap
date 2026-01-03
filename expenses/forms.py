from django import forms
from .models import Expense, Category


class ExpenseForm(forms.ModelForm):
    """
    Formulaire de création et modification de dépenses.
    """
    # Champ catégorie personnalisé pour saisie libre
    category_name = forms.CharField(
        max_length=100,
        required=True,
        label='Catégorie',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: Alimentation, Transport, Loisirs...',
            'list': 'category-suggestions'
        })
    )
    
    class Meta:
        model = Expense
        fields = ('amount', 'description', 'notes', 'date')
        widgets = {
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
                    icon='bi-tag',
                    color='#6c757d'
                )
            
            instance.category = category
        
        if commit:
            instance.save()
        return instance


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
