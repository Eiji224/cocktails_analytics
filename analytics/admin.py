from django.contrib import admin

from .models import CocktailViews


@admin.register(CocktailViews)
class CocktailViewsAdmin(admin.ModelAdmin):
    list_display = ("id", "cocktail", "user", "viewed_at")
    search_fields = ("cocktail__name", "cocktail__id", "user__username", "user__email")
    list_filter = ("viewed_at",)
    autocomplete_fields = ("cocktail", "user")
