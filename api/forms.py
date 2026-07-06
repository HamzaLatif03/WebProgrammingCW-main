from django import forms
from django.contrib.auth import get_user_model
from django.forms import widgets
from django.core.validators import RegexValidator

class CreateUserForm(forms.ModelForm):
    name = forms.CharField(
        required=True,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z\s-]+$',
                message='Name can only contain letters, spaces, and hyphens',
                code='invalid_name'
            )
        ],
        widget=forms.TextInput(attrs={'required': 'required'})
    )
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta:
       model = get_user_model()
       fields = ['username', 'email', 'name', 'date_of_birth', 'password']
       
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        
        return cleaned_data

    def save(self, commit=True):
       user = super().save(commit=False)
       user.set_password(self.cleaned_data["password"]) 
       if commit:
           user.save()
       return user