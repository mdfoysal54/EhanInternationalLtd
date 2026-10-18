from django import forms
from operations.models import Customer

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('kind', 'name', 'phone', 'email', 'country', 'address', 'notes')
        widgets = {'address': forms.Textarea(attrs={'rows': 2}), 'notes': forms.Textarea(attrs={'rows': 2})}

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if not name:
            raise forms.ValidationError('Customer name is required.')
        return name