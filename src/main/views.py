import datetime
import json

import requests
from django.core import serializers
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from user_agent import generate_user_agent

from main.models import InterestCategory, Coord, Result
from main.models.in_house import ApiKey
from main.services import get_points_by_interest_name_service

API_URL = "https://api.vk.com/method/ads.getTargetingStats"
LINK_URL = "https://vk.com/dev/ads.getTargetingStats"
LINK_DOMAIN = "vk.com"


@csrf_exempt
def get_points_json_view(request):
    if request.is_ajax() and request.method == "GET":
        if request.GET.get("interest_name"):
            serialized_instances = serializers.serialize('json', get_points_by_interest_name_service(
                request.GET.get("interest_name")))
            return JsonResponse({"instances": serialized_instances}, status=200)
        else:
            return JsonResponse({"error": "No get parameter interest_name"}, status=400)
    else:
        return JsonResponse({"error": "Unsupported http method"}, status=405)


def test_services(request):
    token = ApiKey.objects.filter(is_taken=False)[0]
    if not token:
        return
    interests = InterestCategory.objects.all().select_related("results")
    points = Coord.objects.all()
    for interest in interests:
        for point in points:
            results_qs = Result.objects.filter(coordinate=point, interest=interest).order_by("-end_date")
            if (datetime.datetime.now() - results_qs[0].end_date).days < 10:
                continue
            criter = {
                "interest_categories": interest.interes_name,
                "geo_near": f"{point.x},{point.y},500"
            }
            json_geo = json.dumps(criter)
            params_dict = {"account_id=": 123, "access_token": token.key, "v": "5.131", "link_url": API_URL,
                           "link_domain": LINK_DOMAIN, "criteria": json_geo}
            response = requests.post(API_URL, params=params_dict, headers=generate_user_agent())
            if response.json().get('error') == 601:
                pass