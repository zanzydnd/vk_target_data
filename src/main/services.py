import datetime
import json

import requests
from user_agent import generate_user_agent

from main.exceptions import TooManyRequestsError
from main.models import Result, InterestCategory, Coord
from main.models.in_house import ApiKey


def get_points_by_interest_name_service(interest_name: str):
    return Result.objects.filter(interest__interes_name=interest_name, count_of_person__gt=0).select_related(
        'coordinate')


API_URL = "https://api.vk.com/method/ads.getTargetingStats"
LINK_URL = "https://vk.com/dev/ads.getTargetingStats"
LINK_DOMAIN = "vk.com"


def make_request_to_api(token: ApiKey, interest: InterestCategory, point: Coord):
    results_qs = Result.objects.filter(coordinate=point, interest=interest).order_by("-end_date")
    if (datetime.datetime.now() - results_qs[0].end_date).days < 10:
        return
    criter = {
        "interest_categories": interest.interes_name,
        "geo_near": f"{point.x},{point.y},500"
    }
    json_geo = json.dumps(criter)
    params_dict = {"account_id=": 123, "access_token": token.key, "v": "5.131", "link_url": API_URL,
                   "link_domain": LINK_DOMAIN, "criteria": json_geo}
    response = requests.post(API_URL, params=params_dict, headers=generate_user_agent())
    if response.json().get("code") == 601:
        raise TooManyRequestsError()
    else:
