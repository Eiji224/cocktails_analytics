from django.db import models
from django.conf import settings

class Cocktail(models.Model):
    name = models.CharField(max_length=255, unique=True)
    instruction = models.TextField()
    is_alcoholic = models.BooleanField()
    image_url = models.URLField()

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    abv = models.IntegerField()
    image_url = models.URLField()

    def __str__(self):
        return self.name


class CocktailIngredient(models.Model):
    cocktail = models.ForeignKey(Cocktail, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    ingredient_measure = models.CharField(max_length=50)

    class Meta:
        unique_together = ('cocktail', 'ingredient')


class CocktailViews(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    cocktail = models.ForeignKey(Cocktail, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)