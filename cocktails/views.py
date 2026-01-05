from django.http import HttpResponse
from django.shortcuts import render

from .models import Cocktail

def chunked(iterable, size):
    for i in range(0, len(iterable), size):
        yield iterable[i:i + size]

def index(request):
    return render(request, 'cocktails/index.html')

def browse_cocktails(request, page: int):
    page_size = 20
    columns = 4

    offset = (page - 1) * page_size

    cocktails = Cocktail.objects.order_by('id')[offset : offset + page_size]
    cocktail_rows = chunked(cocktails, columns)
    context = {
        'cocktail_rows': cocktail_rows,
    }
    return render(request, 'cocktails/cocktails.html', context)