from django import forms
from .models import DigitalMarketing


class DigitalMarketinfForm(forms.ModelForm):
    class Meta:
        model = DigitalMarketing
        fields = ['full_name', 'phone', 'work_name', 'service_choices', 'message']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '09123456789'}),
            'work_name': forms.TextInput(attrs={'class': 'form-control'}),
            'service_choices': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'پیام خود را بنویسید'})
        }
        