from django.core.paginator import Paginator
from django.shortcuts import render

from .models import Cocktail, Ingredient

BROWSE_PAGES_INFO = {
    'items_per_page': 20,
    'items_per_row': 4,
}

def group_into_rows(items, per_row):
    items = list(items)
    return [items[i:i + per_row] for i in range(0, len(items), per_row)]


def index(request):
    return render(request, 'cocktails/index.html')

def browse_cocktails(request, page: int):
    cocktails = Cocktail.objects.order_by('id')
    paginator = Paginator(cocktails, BROWSE_PAGES_INFO.get('items_per_page'))
    page_obj = paginator.get_page(page)

    rows = group_into_rows(page_obj.object_list, BROWSE_PAGES_INFO.get('items_per_row'))

    return render(request, 'cocktails/cocktails.html', {
        'page_obj': page_obj,
        'rows': rows,
    })

def browse_ingredients(request, page: int):
    ingredients = Ingredient.objects.order_by('id')
    paginator = Paginator(ingredients, BROWSE_PAGES_INFO.get('items_per_page'))
    page_obj = paginator.get_page(page)

    rows = group_into_rows(page_obj.object_list, BROWSE_PAGES_INFO.get('items_per_row'))

    return render(request, 'cocktails/ingredients.html', {
        'page_obj': page_obj,
        'rows': rows,
    })