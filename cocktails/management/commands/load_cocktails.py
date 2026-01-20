from django.core.management.base import BaseCommand, CommandError
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
    REQUEST_TIMEOUT = 15

    def add_arguments(self, parser):
        parser.add_argument(
            '--refresh-existing',
            action='store_true',
            help='Перепарсить коктейли, которые уже есть в БД (обновить поля и пересоздать связи ингредиентов)',
        )

    def handle(self, *args, **options):
        env_path = settings.BASE_DIR / '.env'
        load_dotenv(env_path, override=True)

        self.COCKTAIL_BASE_URL = os.getenv('COCKTAIL_URL')
        self.INGREDIENT_BASE_URL = os.getenv('INGREDIENT_URL')

        if not self.COCKTAIL_BASE_URL or not self.INGREDIENT_BASE_URL:
            raise CommandError(
                'COCKTAIL_URL / INGREDIENT_URL не заданы'
                'Проверьте .env или переменные окружения'
            )

        self.refresh_existing = bool(options.get('refresh_existing'))
        self.load_cocktails()

    @staticmethod
    def normalize_name(value):
        if not value:
            return None
        return value.strip()

    @staticmethod
    def normalize_key(value):
        normalized = Command.normalize_name(value)
        return normalized.lower() if normalized else None

    def load_cocktails(self):
        alph = 'abcdefghijklmnopqrstuvwxyz'
        cocktails_ingredients_measure = {}
        connection.ensure_connection()

        self.stdout.write(self.style.NOTICE('Старт загрузки коктейлей'))
        self.process_cocktail(alph, cocktails_ingredients_measure)
        self.process_cocktail_ingredient(cocktails_ingredients_measure)
        self.stdout.write(self.style.SUCCESS('Загрузка коктейлей завершена'))

    def process_cocktail(self, alph, cocktails_ingredients_measure):
        cocktails_to_create = []
        cocktails_to_update = []
        ingredients_to_create = []
        existing_ingredients_lower = {
            key for key in (
                self.normalize_key(name) for name in Ingredient.objects.values_list('name', flat=True)
            ) if key
        }
        existing_cocktails_by_name = {
            self.normalize_name(c.name): c
            for c in Cocktail.objects.only('id', 'name', 'instruction', 'is_alcoholic', 'image_url')
        }
        processed_cocktail_names = set()

        for symbol in alph:
            drinks_cnt = 0
            url = f'{self.COCKTAIL_BASE_URL}{symbol}'

            try:
                resp = requests.get(url, timeout=self.REQUEST_TIMEOUT)
                resp.raise_for_status()
                response = resp.json()
            except requests.RequestException as exc:
                self.stdout.write(
                    self.style.WARNING(f'Ошибка запроса {url}: {exc}')
                )
                continue
            except ValueError:
                self.stdout.write(
                    self.style.WARNING(f'Некорректный JSON из {url}')
                )
                continue

            drinks = response.get('drinks')

            if not drinks:
                self.stdout.write(
                    self.style.WARNING(f'Напитков на букву "{symbol}" не найдено')
                )
                continue

            for drink in drinks:
                if drinks_cnt > 3:
                    break
                drinks_cnt += 1

                cocktail_name = self.normalize_name(drink.get('strDrink'))
                cocktail_key = self.normalize_key(cocktail_name)

                if cocktail_key in processed_cocktail_names:
                    continue

                existing_cocktail = existing_cocktails_by_name.get(cocktail_name)
                if existing_cocktail and not self.refresh_existing:
                    continue

                cocktails_ingredients_measure[cocktail_name] = {}

                if existing_cocktail:
                    existing_cocktail.instruction = drink.get('strInstructions') or ''
                    existing_cocktail.is_alcoholic = drink.get('strAlcoholic') == 'Alcoholic'
                    existing_cocktail.image_url = drink.get('strDrinkThumb') or ''
                    cocktails_to_update.append(existing_cocktail)
                    self.stdout.write(f'Обновляю коктейль: {cocktail_name}')
                else:
                    cocktail = Cocktail(
                        name=cocktail_name,
                        instruction=drink.get('strInstructions') or '',
                        is_alcoholic=drink.get('strAlcoholic') == 'Alcoholic',
                        image_url=drink.get('strDrinkThumb') or '',
                    )
                    cocktails_to_create.append(cocktail)
                    self.stdout.write(f'Новый коктейль: {cocktail_name}')

                processed_cocktail_names.add(cocktail_key)

                for i in range(self.JSON_INGR_IDX_START, self.JSON_INGR_IDX_END):
                    self.process_ingredient(drink, i, existing_ingredients_lower, ingredients_to_create,
                                            cocktails_ingredients_measure)

        Cocktail.objects.bulk_create(cocktails_to_create, batch_size=500, ignore_conflicts=True)
        if cocktails_to_update:
            Cocktail.objects.bulk_update(
                cocktails_to_update,
                fields=['instruction', 'is_alcoholic', 'image_url'],
                batch_size=500,
            )
        unique_ingredients = {}
        for ing in ingredients_to_create:
            key = self.normalize_key(ing.name)
            if key and key not in unique_ingredients:
                unique_ingredients[key] = ing
        Ingredient.objects.bulk_create(unique_ingredients, batch_size=500, ignore_conflicts=True)

    def process_ingredient(self, drink, idx, existing_ingredients_lower, ingredients_to_create,
                           cocktails_ingredients_measure):
        ingredient_name = self.normalize_name(drink.get(f'strIngredient{idx}'))
        ingredient_key = self.normalize_key(ingredient_name)
        measure = drink.get(f'strMeasure{idx}')

        if not ingredient_key:
            return

        if ingredient_key not in self.CREATED_INGREDIENTS and ingredient_key not in existing_ingredients_lower:
            self.create_ingredient(ingredient_name, ingredient_key, ingredients_to_create)

        cocktails_ingredients_measure[self.normalize_name(drink.get('strDrink'))][
            ingredient_name] = measure if measure else 'your taste'

    def process_cocktail_ingredient(self, cocktails_ingredients_measure):
        if not cocktails_ingredients_measure:
            self.stdout.write(self.style.WARNING(
                'Нет данных для связок CocktailIngredient (возможно, все коктейли уже были в БД и --refresh-existing не задан)'))
            return

        target_cocktail_names = set(cocktails_ingredients_measure.keys())
        cocktails = list(Cocktail.objects.filter(name__in=target_cocktail_names).only('id', 'name'))

        all_ingredient_names = set()
        for measures in cocktails_ingredients_measure.values():
            all_ingredient_names.update(measures.keys())

        ingredients_by_name = {}
        for ing in Ingredient.objects.filter(name__in=all_ingredient_names):
            ingredients_by_name[self.normalize_name(ing.name)] = ing

        cocktail_ingredients_to_create = []
        for cocktail in cocktails:
            measure_data = cocktails_ingredients_measure.get(cocktail.name, {})
            for ingredient_name, measure in measure_data.items():
                ingredient = ingredients_by_name.get(ingredient_name)
                if ingredient is None:
                    self.stdout.write(f"Warning: Ingredient '{ingredient_name}' not found in DB!")
                    continue
                cocktail_ingredients_to_create.append(
                    CocktailIngredient(
                        cocktail=cocktail,
                        ingredient=ingredient,
                        ingredient_measure=measure,
                    )
                )

        CocktailIngredient.objects.filter(cocktail__in=cocktails).delete()
        CocktailIngredient.objects.bulk_create(cocktail_ingredients_to_create, batch_size=500)

    def create_ingredient(self, name, ingredients_to_create):
        resp = requests.get(self.INGREDIENT_BASE_URL + name).json()
        ingredients = resp.get('ingredients')

        data = ingredients[0] if ingredients else {}
        abv = data.get('strABV')
        description = data.get('strDescription')

        ingredients_to_create.append(
            Ingredient(
                name=name,
                description=description if description else '',
                abv=int(abv) if abv else 0,
                image_url=f'{os.getenv('INGREDIENT_IMAGE_URL')}/{name}.png'
            )
        )
        key = self.normalize_key(name)
        if key:
            self.CREATED_INGREDIENTS.add(key)