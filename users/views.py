from django.shortcuts import render, redirect
from . import forms

def register(request):
    if request.method == 'POST':
        form = forms.CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = forms.CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})