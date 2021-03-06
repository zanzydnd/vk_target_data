from django.urls import path

from main.views import get_points_json_view, get_map_template

urlpatterns = [
    path("",get_map_template, name="map_template"),
    path("points/", get_points_json_view, name="get_points"),
]
