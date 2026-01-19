from django.shortcuts import render
from .services import cocktail_service


def browse_most_viewed_cocktails(request):
    most_viewed = cocktail_service.get_most_viewed_cocktails()

    return render(request, 'analytics/most_viewed_cocktails.html', {'most_viewed': most_viewed})