from django import forms
from .models import Role, Platform, ModularPlatform, FixedPlatform, Card

class RoleSelectionForm(forms.Form):
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        label="Select a Role",
        required=True
    )

class PlatformSelectionForm(forms.Form):
    platform = forms.ModelChoiceField(
        queryset=Platform.objects.none(),
        label="Select a Platform",
        required=True
    )

    def __init__(self, *args, **kwargs):
        role = kwargs.pop('role', None)
        super().__init__(*args, **kwargs)
        if role:
            self.fields['platform'].queryset = role.allowed_platforms.all()

class HostnameLoopbackForm(forms.Form):
    hostname = forms.CharField(max_length=64, required=True)
    loopback = forms.GenericIPAddressField(required=True)

class CardSelectionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        platform = kwargs.pop('platform', None)
        super().__init__(*args, **kwargs)
        if platform and isinstance(platform, ModularPlatform):
            for slot_num in range(1, platform.num_slots + 1):
                card_queryset = platform.supported_cards.all()
                choices = [(None, 'No Card')] + [(c.id, f"{c.brand} {c.model}") for c in card_queryset]
                self.fields[f"slot_{slot_num}"] = forms.ChoiceField(
                    choices=choices, 
                    required=False, 
                    label=f"Slot {slot_num} Card"
                )

class CoreParamsForm(forms.Form):
    hostname = forms.CharField(max_length=64, required=True)
    lo0_ip = forms.GenericIPAddressField(required=True, label="Loopback IP (no CIDR mask)")
    uplink_iface = forms.CharField(max_length=64, required=True, label="Uplink Interface")
    uplink_ip_cidr = forms.CharField(max_length=64, required=True, label="Uplink IP (with CIDR)")

class MarketParamsForm(forms.Form):
    hostname = forms.CharField(max_length=64, required=True)
    lo0_ip = forms.GenericIPAddressField(required=True, label="Loopback IP (no CIDR mask)")
    uplink_iface = forms.CharField(max_length=64, required=True, label="Uplink Interface")
    uplink_ip_cidr = forms.CharField(max_length=64, required=True, label="Uplink IP (with CIDR)")

class EdgeParamsForm(forms.Form):
    hostname = forms.CharField(max_length=64, required=True)
    lo0_ip = forms.GenericIPAddressField(required=True, label="Loopback IP (no CIDR mask)")
    asn = forms.IntegerField(required=True, label="BGP ASN")

