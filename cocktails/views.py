from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Cocktail, Ingredient, CocktailIngredient, FavouriteCocktail

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

def explore_cocktail(request, id: int):
    cocktail = Cocktail.objects.get(id=id)
    cocktail_ingredients = CocktailIngredient.objects.filter(cocktail_id=id)

    ingredients = {}
    for ci in cocktail_ingredients:
        ingredient = Ingredient.objects.get(id=ci.ingredient_id)
        ingredients[ingredient] = ci.ingredient_measure

    return render(request, 'cocktails/explore_cocktail.html', {
        'cocktail': cocktail,
        'ingredients': list(ingredients.items()),
    })

def explore_ingredient(request, id: int):
    ingredient = Ingredient.objects.get(id=id)
    cocktail_ingredients = CocktailIngredient.objects.filter(ingredient_id=id)

    cocktails = [Cocktail.objects.get(id=ci.cocktail_id) for ci in cocktail_ingredients]

    return render(request, 'cocktails/explore_ingredient.html', {
        'ingredient': ingredient,
        'cocktails': cocktails,
    })

@login_required
def toggle_favourite(request, cocktail_id: int):
    cocktail = get_object_or_404(Cocktail, id=cocktail_id)

    favourite, created = FavouriteCocktail.objects.get_or_create(
        user=request.user,
        cocktail=cocktail,
    )

    if not created:
        favourite.delete()

    return redirect(request.META.get('HTTP_REFERER', '/'))