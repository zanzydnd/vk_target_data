from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from main.models import InterestCategory
from main.services import get_points_by_interest_name_service, pick_points

AGES = [(14, 18), (18, 21), (21, 24),
        (24, 27), (27, 30), (30, 35), (35, 45), (45, 54), (54, 65), (65, 80)]


@csrf_exempt
def get_points_json_view(request):
    if request.is_ajax() and request.method == "GET":
        if request.GET.get("interest"):
            serialized_instances = serializers.serialize('json', pick_points(
                request.GET.get("interest"), request.GET.get("sex"), request.GET.get("age")),
                                                         use_natural_foreign_keys=True, use_natural_primary_keys=True)
            return JsonResponse({"instances": serialized_instances}, status=200)
        else:
            return JsonResponse({"error": "No get parameter interest"}, status=400)
    else:
        return JsonResponse({"error": "Unsupported http method"}, status=405)


def get_map_template(request):
    return render(request, "map_template.html", {"interests": InterestCategory.objects.all(), "ages": AGES})
