import datetime
import json

import requests
from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from main.models import InterestCategory, Coord
from main.services import get_points_by_interest_name_service, make_request_to_api


@csrf_exempt
def get_points_json_view(request):
    if request.is_ajax() and request.method == "GET":
        if request.GET.get("interest"):
            serialized_instances = serializers.serialize('json', get_points_by_interest_name_service(
                request.GET.get("interest")), use_natural_foreign_keys=True, use_natural_primary_keys=True)
            print(serialized_instances)
            return JsonResponse({"instances": serialized_instances}, status=200)
        else:
            return JsonResponse({"error": "No get parameter interest"}, status=400)
    else:
        return JsonResponse({"error": "Unsupported http method"}, status=405)


def get_map_template(request):
    return render(request, "map_template.html")


def test_services(request):
    interests = InterestCategory.objects.all().select_related("results")
    points = Coord.objects.all()
    for interest in interests:
        for point in points:
            make_request_to_api(interest, point, try_num=1, err_cnt=0)
