from cocktails.models import Cocktail, CocktailViews

class CocktailViewMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if '/cocktail/' in request.path:
            path_parts = request.path.strip('/').split('/')
            if len(path_parts) >= 2 and path_parts[0] == 'cocktail':
                cocktail_id = int(path_parts[1])
                cocktail = Cocktail.objects.get(id=cocktail_id)
                user = request.user if request.user.is_authenticated else None

                try:
                    CocktailViews.objects.create(
                        user=user,
                        cocktail=cocktail,
                    )
                except ValueError:
                    pass

                request.cocktail = cocktail

        response = self.get_response(request)
        return response