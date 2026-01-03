from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile


class UserRegistrationForm(UserCreationForm):
    """
    Formulaire d'inscription avec champs supplémentaires.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Prénom'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom d\'utilisateur'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajouter la classe Bootstrap aux champs de mot de passe
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Mot de passe'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmer le mot de passe'
        })

    def clean_email(self):
        """Valider l'unicité de l'email"""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "Un compte avec cet email existe déjà. "
                "Veuillez utiliser un autre email ou réinitialiser votre mot de passe."
            )
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    """
    Formulaire de mise à jour des informations de l'utilisateur.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean_email(self):
        """Valider l'unicité de l'email (sauf pour l'utilisateur actuel)"""
        email = self.cleaned_data.get('email')
        if email:
            # Exclure l'utilisateur actuel de la vérification
            users_with_email = User.objects.filter(email=email).exclude(pk=self.instance.pk)
            if users_with_email.exists():
                raise forms.ValidationError(
                    "Un autre compte utilise déjà cet email."
                )
        return email


class ProfileUpdateForm(forms.ModelForm):
    """
    Formulaire de mise à jour du profil utilisateur.
    """
    class Meta:
        model = UserProfile
        fields = ('phone_number', 'date_of_birth', 'avatar', 'theme_preference')
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+237 6XX XX XX XX'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'theme_preference': forms.Select(attrs={
                'class': 'form-select'
            })
        }
