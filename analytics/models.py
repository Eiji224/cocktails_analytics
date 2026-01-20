from django.db import models
from django.conf import settings

class CocktailViews(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    cocktail = models.ForeignKey('cocktails.Cocktail', on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)