from django.contrib import admin

from .models import Cocktail, Ingredient, CocktailIngredient, FavouriteCocktail


@admin.register(Cocktail)
class CocktailAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_alcoholic", "image_url")
    search_fields = ("name", "id")
    list_filter = ("is_alcoholic",)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "abv", "image_url")
    search_fields = ("name", "id")
    list_filter = ("abv",)


@admin.register(CocktailIngredient)
class CocktailIngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "cocktail", "ingredient", "ingredient_measure")
    search_fields = ("cocktail__name", "ingredient__name", "cocktail__id", "ingredient__id")
    autocomplete_fields = ("cocktail", "ingredient")


@admin.register(FavouriteCocktail)
class FavouriteCocktailAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "cocktail")
    search_fields = ("user__username", "user__email", "cocktail__name", "cocktail__id")
    autocomplete_fields = ("user", "cocktail")
