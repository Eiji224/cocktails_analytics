from django.urls import path
from .views import browse_most_viewed_cocktails

urlpatterns = [
    path('cocktails', browse_most_viewed_cocktails, name='most_viewed_cocktails'),
]