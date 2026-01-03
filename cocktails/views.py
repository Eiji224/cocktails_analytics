from django.http import HttpResponse
from django.shortcuts import render

from .models import Cocktail

def index(request):
    return render(request, 'cocktails/index.html')