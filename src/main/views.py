import datetime
import json

import requests
from django.core import serializers
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from user_agent import generate_user_agent

from main.exceptions import TooManyRequestsError
from main.models import InterestCategory, Coord, Result
from main.models.in_house import ApiKey
from main.services import get_points_by_interest_name_service, make_request_to_api


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
            try:
                make_request_to_api(token, interest, point)
            except TooManyRequestsError as tmn_e:
                pass
