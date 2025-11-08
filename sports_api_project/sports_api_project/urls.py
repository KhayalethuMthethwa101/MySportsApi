from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    
    # This line sends any URL starting with 'api/premier-league/'
    # to be handled by our 'premier_league' app's urls.py file.
    path('api/premier-league/', include('premier_league_service.urls')),
]