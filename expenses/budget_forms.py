from django import forms
from .models import Budget, Category
from datetime import datetime


class BudgetForm(forms.ModelForm):
    """
    Formulaire pour créer ou modifier un budget.
    """
    class Meta:
        model = Budget
        fields = ['category', 'amount', 'month', 'year', 'alert_threshold']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-select',
                'required': False
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 50000',
                'min': '0',
                'step': '0.01'
            }),
            'month': forms.Select(attrs={
                'class': 'form-select'
            }),
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '2020',
                'max': '2050'
            }),
            'alert_threshold': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100',
                'value': '80'
            })
        }
        labels = {
            'category': 'Catégorie (vide = budget global)',
            'amount': 'Montant du budget (FCFA)',
            'month': 'Mois',
            'year': 'Année',
            'alert_threshold': 'Seuil d\'alerte (%)'
        }
        help_texts = {
            'category': 'Laissez vide pour un budget global (toutes catégories)',
            'alert_threshold': 'Vous serez alerté quand ce pourcentage est atteint'
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Choix des mois
        MONTHS = [
            (1, 'Janvier'), (2, 'Février'), (3, 'Mars'), (4, 'Avril'),
            (5, 'Mai'), (6, 'Juin'), (7, 'Juillet'), (8, 'Août'),
            (9, 'Septembre'), (10, 'Octobre'), (11, 'Novembre'), (12, 'Décembre')
        ]
        self.fields['month'].widget.choices = MONTHS
        
        # Valeurs par défaut
        if not self.instance.pk:
            today = datetime.now()
            self.fields['month'].initial = today.month
            self.fields['year'].initial = today.year
    
    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        month = cleaned_data.get('month')
        year = cleaned_data.get('year')
        
        # Vérifier si un budget existe déjà pour cette combinaison
        if self.user and month and year:
            existing = Budget.objects.filter(
                user=self.user,
                category=category,
                month=month,
                year=year
            )
            
            # Exclure l'instance actuelle en cas de modification
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                cat_name = category.name if category else "global"
                raise forms.ValidationError(
                    f"Un budget {cat_name} existe déjà pour {month}/{year}"
                )
        
        return cleaned_data
