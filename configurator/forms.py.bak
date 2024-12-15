# configurator/forms.py
from django import forms
from .models import Role, Platform

class RoleSelectionForm(forms.Form):
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        label="Select a Role",
        required=True
    )

class PlatformSelectionForm(forms.Form):
    # This form will be dynamically populated later in the view based on selected role
    platform = forms.ModelChoiceField(
        queryset=Platform.objects.none(),
        label="Select a Platform",
        required=True
    )

