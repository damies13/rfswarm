# my_time_api/urls.py
from django.contrib import admin
from django.urls import path, include # Import 'include'

urlpatterns = [
    # path('admin/', admin.site.urls),
    # --- Add this line to include the API app routes ---
    path('api/v1/', include('RFSwarmDjango.api_v1.urls')),
]
