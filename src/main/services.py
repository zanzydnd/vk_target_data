import datetime
import json
import time

import requests
from django.utils import timezone
from user_agent import generate_user_agent

from main.exceptions import TooManyRequestsError
from main.models import Result, InterestCategory, Coord
from main.models.in_house import ApiKey, Pairs


def get_points_by_interest_name_service(interest_name: str):
    date_10_days_ago = timezone.now() - datetime.timedelta(days=10)
    return Result.objects.filter(interest__interes_name=interest_name, count_of_person__gt=0,
                                 end_date__gte=date_10_days_ago).select_related(
        'coordinate')


API_URL = "https://api.vk.com/method/ads.getTargetingStats"
LINK_URL = "https://vk.com/dev/ads.getTargetingStats"
LINK_DOMAIN = "vk.com"


def make_request_to_api(interest: InterestCategory, point: Coord, try_num: int, err_cnt: int):
    if err_cnt >= 10:
        return
    try:
        token = ApiKey.objects.filter(expired=False)[try_num - 1]
    except IndexError as e:
        return
    if not token:
        return
    results_qs = Result.objects.filter(coordinate=point, interest=interest).order_by("-end_date")
    if results_qs and (timezone.now() - results_qs[0].end_date).days < 10:
        return
    entity = Result(begin_date=timezone.now())
    criter = {
        "interest_categories": interest.interes_name,
        "geo_near": f"{point.y},{point.x},500"
    }
    # latitude - широта - y
    # longitude - долгота - x
    json_geo = json.dumps(criter)
    params_dict = {"account_id": token.acc_id, "access_token": token.key, "v": "5.131", "link_url": API_URL,
                   "link_domain": LINK_DOMAIN, "criteria": json_geo}
    response = requests.post(API_URL, params=params_dict, headers={"User_Agent": generate_user_agent()})
    print(response.json())
    time.sleep(20)
    if response.json().get("error"):
        if response.json().get("error_code") == 601:
            make_request_to_api(interest, point, try_num=try_num + 1, err_cnt=err_cnt)
        else:
            time.sleep(1000)
            make_request_to_api(interest, point, try_num, err_cnt=err_cnt + 1)
    else:
        response_data = response.json()['response']
        entity.interest = interest
        entity.coordinate = point
        entity.link = API_URL
        entity.count_of_person = response_data['audience_count']
        pair = Pairs.objects.get(point=point, interest=interest)
        pair.last_executions = timezone.now()
        pair.save()
        entity.save()
