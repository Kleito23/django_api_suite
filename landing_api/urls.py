from django.urls import path

from .views import LandingAPI


urlpatterns = [
    path("index/", LandingAPI.as_view(), name="landing_api"),
]