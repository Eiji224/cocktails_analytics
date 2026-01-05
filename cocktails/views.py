from django.core.paginator import Paginator
from django.shortcuts import render

from .models import Cocktail

def index(request):
    return render(request, 'cocktails/index.html')

def browse_cocktails(request, page: int):
    elements_qty = 20
    items_per_row = 4

    cocktails = Cocktail.objects.order_by('id')
    paginator = Paginator(cocktails, elements_qty)
    page_obj = paginator.get_page(page)

    def group_into_rows(items, per_row):
        items = list(items)
        return [items[i:i + per_row] for i in range(0, len(items), per_row)]

    rows = group_into_rows(page_obj.object_list, items_per_row)

    return render(request, 'cocktails/cocktails.html', {
        'page_obj': page_obj,
        'rows': rows,
    })