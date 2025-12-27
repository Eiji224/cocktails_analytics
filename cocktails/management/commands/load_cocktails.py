from django.core.management.base import BaseCommand
import requests
from cocktails.models import Cocktail, Ingredient, CocktailIngredient


class Command(BaseCommand):
    help = 'Load cocktails from TheCocktailDB API'

    COCKTAIL_BASE_URL = 'https://www.thecocktaildb.com/api/json/v1/1/search.php?f='
    INGREDIENT_BASE_URL = 'https://www.thecocktaildb.com/api/json/v1/1/search.php?i='

    JSON_INGR_IDX_START = 1
    JSON_INGR_IDX_END = 16

    CREATED_INGREDIENTS = set()

    def handle(self, *args, **options):
        self.load_cocktails()

    def load_cocktails(self):
        alph = 'abcdefghijklmnopqrstuvwxyz'
        cocktails_ingredients_measure = {}

        self.process_cocktail(alph, cocktails_ingredients_measure)

        cocktails = Cocktail.objects.all()
        ingredients = Ingredient.objects.all()

        self.process_cocktail_ingredient(cocktails, ingredients, cocktails_ingredients_measure)

    def process_cocktail(self, alph, cocktails_ingredients_measure):
        for symbol in alph:
            cocktails_to_create = []
            ingredients_to_create = []

            response = requests.get(self.COCKTAIL_BASE_URL + symbol).json()
            drinks = response.get('drinks')

            if not drinks:
                continue

            for drink in drinks:
                cocktail = Cocktail(
                    name=drink['strDrink'],
                    instruction=drink['strInstructions'],
                    is_alcoholic=drink['strAlcoholic'] == 'Alcoholic',
                    image_url=drink['strDrinkThumb'],
                )
                cocktails_ingredients_measure[cocktail.name] = {}
                cocktails_to_create.append(cocktail)

                for i in range(self.JSON_INGR_IDX_START, self.JSON_INGR_IDX_END):
                    self.process_ingredient(drink, i, cocktail, ingredients_to_create, cocktails_ingredients_measure)

            Cocktail.objects.bulk_create(cocktails_to_create)
            Ingredient.objects.bulk_create(ingredients_to_create)

    def process_ingredient(self, drink, idx, ingredients_to_create, cocktails_ingredients_measure):
        ingredient_name = drink.get(f'strIngredient{idx}')
        measure = drink.get(f'strMeasure{idx}')

        if not ingredient_name:
            return

        ingredient = self.get_or_create_ingredient(ingredient_name, ingredients_to_create)
        cocktails_ingredients_measure[drink.get('strDrink')][ingredient.name] = measure

    def process_cocktail_ingredient(self, cocktails, ingredients, cocktails_ingredients_measure):
        for cocktail in cocktails:
            measure_data = cocktails_ingredients_measure[cocktail.name]
            cocktail_ingredients_to_create = []

            for ingredient_name, measure in measure_data.items():
                for ingredient in ingredients:
                    if ingredient.name != ingredient_name:
                        continue

                    cocktail_ingredients_to_create.append(
                        CocktailIngredient(
                            cocktail=cocktail,
                            ingredient=ingredient,
                            ingredient_measure=measure,
                        )
                    )

            CocktailIngredient.objects.bulk_create(cocktail_ingredients_to_create)

    def get_or_create_ingredient(self, name, ingredients_to_create):
        if self.CREATED_INGREDIENTS.__contains__(name):
            return Ingredient.objects.get(name=name)

        resp = requests.get(self.INGREDIENT_BASE_URL + name).json()
        ingredients = resp.get('ingredients')
        self.CREATED_INGREDIENTS.add(name)

        data = ingredients[0] if ingredients else {}
        abv = int(data.get('strABV')) if ingredients else 0
        description = data.get('strDescription') if ingredients else ''

        ingredient, _ = Ingredient.objects.get_or_create(
            name=data['strIngredient'],
            defaults={
                'description': description,
                'abv': abv,
                'image_url': f'https://www.thecocktaildb.com/images/ingredients/{name}.png'
            }
        )

        ingredients_to_create.append(ingredient)
        return ingredient