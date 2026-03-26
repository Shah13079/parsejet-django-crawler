from django import forms
from django.forms.models import ModelForm
from .models import Account

class Registration(ModelForm):
    password=forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':"Password"
    }))

    Repeat_password=forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':"Enter Password again"
    }))


    class Meta:
        model=Account
        fields=['first_name','last_name','email','username','password','Repeat_password']

    def __init__(self,*args,**kwargs):
        super(Registration,self).__init__(*args,**kwargs)
        self.fields['first_name'].widget.attrs['placeholder']=' Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder']=' Enter Last Name'
        self.fields['email'].widget.attrs['placeholder']='Email'
        self.fields['username'].widget.attrs['placeholder']='username'
        self.fields['password'].widget.attrs['placeholder']='Password'


        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'


    def clean(self):
        cleaned_data=super(Registration,self).clean()
        password=cleaned_data.get('password')
        Repeat_password=cleaned_data.get("Repeat_password")

        if password != Repeat_password:
            raise forms.ValidationError(
                "password does not match!"
            )

class Profile_update(forms.ModelForm):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    # email = forms.CharField(required=False)
    about_you = forms.CharField(required=False)
    address = forms.CharField(required=False)

    class Meta:
        model=Account
        fields=['first_name','last_name','about_you','address']
