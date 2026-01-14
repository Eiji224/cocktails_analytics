from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control form-control-lg',
                'placeholder': self.fields[field_name].label or field_name.capitalize()
            })

        self.fields['username'].widget.attrs.update({
            'placeholder': 'Enter your username',
            'autofocus': True
        })
        self.fields['email'].widget.attrs.update({
            'placeholder': 'your.email@example.com'
        })
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Create a strong password'
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirm your password'
        })

        self.fields['password1'].help_text = (
            '<small class="form-text text-white">'
            'Your password must contain at least 8 characters, '
            'not be commonly used, and not be entirely numeric.'
            '</small>'
        )
        self.fields['password2'].help_text = ''