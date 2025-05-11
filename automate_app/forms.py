from django import forms
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _

class PersonneForm(forms.Form):
    nom = forms.CharField(
        label=_("Nom"),
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Votre nom de famille')
        })
    )
    
    prenom = forms.CharField(
        label=_("Prénom"),
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Votre prénom')
        })
    )
    
    date_naissance = forms.DateField(
        label=_("Date de naissance"),
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        help_text=_("Format: JJ/MM/AAAA")
    )

    def clean(self):
        cleaned_data = super().clean()
        # Vous pourriez ajouter ici des validations croisées si nécessaire
        return cleaned_data
    

class UploadCSVForm(forms.Form):
    fichier_csv = forms.FileField(
        label='Fichier CSV à traiter',
        help_text='Format attendu : nom, prénom, date_naissance (dd/mm/yyyy)',
        validators=[FileExtensionValidator(allowed_extensions=['csv'])],
        widget=forms.FileInput(attrs={
            'accept': '.csv',
            'class': 'form-control-file'
        })
    )
    
    def clean_fichier_csv(self):
        fichier = self.cleaned_data['fichier_csv']
        if fichier.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Le fichier est trop volumineux (max 5MB)")
        return fichier