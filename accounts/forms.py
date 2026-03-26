"""Django forms for user registration and profile management."""
from django import forms
from django.forms.models import ModelForm
from .models import Account


class Registration(ModelForm):
    """Registration form with password confirmation validation."""

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Password'
    }))

    repeat_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter Password again'
    }))

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email', 'username', 'password', 'repeat_password']

    def __init__(self, *args, **kwargs):
        super(Registration, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = ' Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = ' Enter Last Name'
        self.fields['email'].widget.attrs['placeholder'] = 'Email'
        self.fields['username'].widget.attrs['placeholder'] = 'username'
        self.fields['password'].widget.attrs['placeholder'] = 'Password'

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super(Registration, self).clean()
        password = cleaned_data.get('password')
        repeat_password = cleaned_data.get('repeat_password')

        if password != repeat_password:
            raise forms.ValidationError(
                'Password does not match!'
            )


class ProfileUpdate(forms.ModelForm):
    """Form for updating user profile fields."""

    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    about_you = forms.CharField(required=False)
    address = forms.CharField(required=False)

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'about_you', 'address']
