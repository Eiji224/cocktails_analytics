from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cocktails/<int:page>', views.browse_cocktails, name='cocktails'),
    path('ingredients/<int:page>', views.browse_ingredients, name='ingredients'),
    path('cocktail/<int:id>', views.explore_cocktail, name='explore_cocktail'),
    path('ingredient/<int:id>', views.explore_ingredient, name='explore_ingredient'),
    path('favourites/toggle/<int:cocktail_id>', views.toggle_favourite, name='toggle_favourite'),
    path('favourites/<int:page>', views.checkout_favourites, name='favourites'),
]