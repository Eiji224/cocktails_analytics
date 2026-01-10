from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cocktails/<int:page>', views.browse_cocktails, name='cocktails'),
    path('ingredients/<int:page>', views.browse_ingredients, name='ingredients'),
    path('cocktail/<int:id>', views.explore_cocktail, name='explore_cocktail')
]