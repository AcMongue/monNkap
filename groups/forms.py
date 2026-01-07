from django import forms
from django.contrib.auth.models import User
from .models import Group, Membership, GroupContribution, GroupExpense, GroupSavingsGoal, GroupSavingsContribution


class GroupForm(forms.ModelForm):
    """
    Formulaire de création et modification de groupes.
    """
    class Meta:
        model = Group
        fields = ('name', 'description', 'target_amount', 'deadline', 'status')
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Projet voyage à Dubaï'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Décrivez l\'objectif du groupe...'
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
        # Pour un nouveau groupe, ne pas afficher le champ status
        if not self.instance.pk:
            self.fields.pop('status')


class MembershipForm(forms.Form):
    """
    Formulaire d'ajout de membres à un groupe par recherche de nom d'utilisateur.
    """
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez le nom d\'utilisateur',
            'autocomplete': 'off'
        }),
        label='Nom d\'utilisateur'
    )
    
    role = forms.ChoiceField(
        choices=Membership.ROLE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Rôle',
        initial='member'
    )
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        try:
            user = User.objects.get(username=username)
            return user
        except User.DoesNotExist:
            raise forms.ValidationError(f"L'utilisateur '{username}' n'existe pas.")


class GroupContributionForm(forms.ModelForm):
    """
    Formulaire d'ajout de contribution à un groupe.
    """
    class Meta:
        model = GroupContribution
        fields = ('amount', 'note', 'date')
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Montant à contribuer',
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


class GroupExpenseForm(forms.ModelForm):
    """
    Formulaire d'ajout de dépense de groupe.
    """
    class Meta:
        model = GroupExpense
        fields = ('category', 'amount', 'description', 'date')
        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Montant de la dépense',
                'step': '0.01',
                'min': '0.01'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Description de la dépense'
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


class GroupSavingsGoalForm(forms.ModelForm):
    """
    Formulaire de création d'objectif d'épargne de groupe.
    """
    class Meta:
        model = GroupSavingsGoal
        fields = ('title', 'description', 'target_amount', 'deadline')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Voyage à Paris, Investissement immobilier...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Décrivez votre objectif d\'épargne commune...'
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
            })
        }


class GroupSavingsContributionForm(forms.ModelForm):
    """
    Formulaire d'ajout de contribution à un objectif d'épargne de groupe.
    """
    class Meta:
        model = GroupSavingsContribution
        fields = ('amount', 'note', 'date')
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Montant à contribuer',
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
