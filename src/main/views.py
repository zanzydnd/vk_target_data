from django.core import serializers
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from main.services import get_points_by_interest_name_service


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
