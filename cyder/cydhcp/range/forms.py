from django import forms

from cyder.cydhcp.range.models import Range, RangeKeyValue
from cyder.base.mixins import UsabilityFormMixin


class RangeForm(forms.ModelForm, UsabilityFormMixin):
    class Meta:
        model = Range
        exclude = ('start_upper', 'start_lower', 'end_upper', 'end_lower')
        fields = ('network', 'ip_type', 'start_str', 'end_str', 'domain',
                  'is_reserved', 'allow', 'views', 'dhcpd_raw_include',
                  'dhcp_enabled')
        widgets = {'views': forms.CheckboxSelectMultiple,
                   'ip_type': forms.RadioSelect}

    def __init__(self, *args, **kwargs):
        super(RangeForm, self).__init__(*args, **kwargs)
        self.fields['dhcpd_raw_include'].label = "DHCP Config Extras"
        self.fields['dhcpd_raw_include'].widget.attrs.update(
            {'cols': '80',
             'style': 'display: none;width: 680px'})


class RangeKeyValueForm(forms.ModelForm):
    range = forms.ModelChoiceField(
        queryset=Range.objects.all(),
        widget=forms.HiddenInput())

    class Meta:
        model = RangeKeyValue
        exclude = ('is_option', 'is_statement', 'is_quoted')
