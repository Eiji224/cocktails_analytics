from django.core.management.base import BaseCommand
from django.db import connection
from cocktails.models import Cocktail, Ingredient, CocktailIngredient
from django.conf import settings
import requests
import os
from dotenv import load_dotenv


class Command(BaseCommand):
    help = 'Load cocktails from TheCocktailDB API'

    JSON_INGR_IDX_START = 1
    JSON_INGR_IDX_END = 16

    CREATED_INGREDIENTS = set()

    def handle(self, *args, **options):
        env_path = settings.BASE_DIR / '.env'
        load_dotenv(env_path, override=True)

        self.COCKTAIL_BASE_URL = os.getenv('COCKTAIL_URL')
        self.INGREDIENT_BASE_URL = os.getenv('INGREDIENT_URL')
        
        self.load_cocktails()

    def load_cocktails(self):
        alph = 'abcdefghijklmnopqrstuvwxyz'
        cocktails_ingredients_measure = {}
        connection.ensure_connection()

        self.process_cocktail(alph, cocktails_ingredients_measure)

        cocktails = Cocktail.objects.all()

        self.process_cocktail_ingredient(cocktails, cocktails_ingredients_measure)

    def process_cocktail(self, alph, cocktails_ingredients_measure):
        cocktails_to_create = []
        ingredients_to_create = []
        existing_ingredients = set(
            Ingredient.objects.values_list('name', flat=True)
        )
        existing_cocktails = set(
            Cocktail.objects.values_list('name', flat=True)
        )
        processed_cocktail_names = set()

        for symbol in alph:
            drinks_cnt = 0
            response = requests.get(self.COCKTAIL_BASE_URL + symbol).json()
            drinks = response.get('drinks')

            if not drinks:
                continue

            for drink in drinks:
                if drinks_cnt > 3:
                    break
                drinks_cnt += 1

                cocktail_name = drink['strDrink']

                if cocktail_name in processed_cocktail_names or cocktail_name in existing_cocktails:
                    continue

                cocktail = Cocktail(
                    name=cocktail_name,
                    instruction=drink['strInstructions'],
                    is_alcoholic=drink['strAlcoholic'] == 'Alcoholic',
                    image_url=drink['strDrinkThumb'],
                )
                cocktails_ingredients_measure[cocktail.name] = {}
                cocktails_to_create.append(cocktail)
                processed_cocktail_names.add(cocktail_name)

                print(cocktail.name)

                for i in range(self.JSON_INGR_IDX_START, self.JSON_INGR_IDX_END):
                    self.process_ingredient(drink, i, existing_ingredients, ingredients_to_create,
                                            cocktails_ingredients_measure)

        Cocktail.objects.bulk_create(cocktails_to_create, batch_size=500, ignore_conflicts=True)
        Ingredient.objects.bulk_create(ingredients_to_create, batch_size=500, ignore_conflicts=True)

    def process_ingredient(self, drink, idx, existing_ingredients, ingredients_to_create,
                           cocktails_ingredients_measure):
        ingredient_name = drink.get(f'strIngredient{idx}')
        measure = drink.get(f'strMeasure{idx}')

        if not ingredient_name:
            return

        if not self.CREATED_INGREDIENTS.__contains__(ingredient_name) and not ingredient_name in existing_ingredients:
            self.create_ingredient(ingredient_name, ingredients_to_create)

        cocktails_ingredients_measure[drink.get('strDrink')][ingredient_name] = measure if measure else 'your taste'

    def process_cocktail_ingredient(self, cocktails, cocktails_ingredients_measure):
        ingredients_by_name = {
            ing.name: ing
            for ing in Ingredient.objects.filter(name__in=self.CREATED_INGREDIENTS)
        }

        cocktail_ingredients_to_create = []
        for cocktail in cocktails:
            measure_data = cocktails_ingredients_measure.get(cocktail.name, {})

            for ingredient_name, measure in measure_data.items():
                ingredient = ingredients_by_name[ingredient_name]
                cocktail_ingredients_to_create.append(
                    CocktailIngredient(
                        cocktail=cocktail,
                        ingredient=ingredient,
                        ingredient_measure=measure,
                    )
                )

        CocktailIngredient.objects.bulk_create(cocktail_ingredients_to_create, batch_size=500)

    def create_ingredient(self, name, ingredients_to_create):
        resp = requests.get(self.INGREDIENT_BASE_URL + name).json()
        ingredients = resp.get('ingredients')
        self.CREATED_INGREDIENTS.add(name)

        data = ingredients[0] if ingredients else {}
        abv = data.get('strABV')
        description = data.get('strDescription')

        ingredients_to_create.append(
            Ingredient(
                name=name,
                description=description if description else '',
                abv=int(abv) if abv else 0,
                image_url=f'https://www.thecocktaildb.com/images/ingredients/{name}.png'
            )
        )