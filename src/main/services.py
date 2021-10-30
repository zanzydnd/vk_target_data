import django

django.setup()

import asyncio
import datetime
import json
import multiprocessing

import aiohttp
import requests
from django.db.models import Q
from django.utils import timezone
from user_agent import generate_user_agent

from main.models import Result
from main.models.in_house import ApiKey, Pairs, PairsWithSexAndAge


def get_points_by_interest_name_service(interest_name: str):
    date_10_days_ago = timezone.now() - datetime.timedelta(days=10)
    # left = int(batch) * 1000
    # right = left + 1000
    return Result.objects.filter(interest__interes_name=interest_name, count_of_person__gt=0,
                                 end_date__gte=date_10_days_ago).select_related(
        'coordinate')  # [left:right]


API_URL = "https://api.vk.com/method/ads.getTargetingStats"
LINK_URL = "https://vk.com/dev/ads.getTargetingStats"
LINK_DOMAIN = "vk.com"


async def parser(token, pairs):
    result = []
    for pair in pairs:
        point = pair.point
        interest = pair.interest
        token.is_taken = True
        token.save()
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
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, params=params_dict) as response:
                response_json = await response.json()
                try:
                    print(multiprocessing.current_process())
                except Exception:
                    pass
                print(token.key)
                print(response_json)
                await asyncio.sleep(5)
                if response_json.get('error'):
                    if response_json.get('error_code') == 601:
                        token.is_taken = False
                        token.expired = True
                        token.save()
                    else:
                        continue
                else:
                    response_data = response_json.get('response')
                    entity.interest = interest
                    entity.coordinate = point
                    entity.link = API_URL
                    entity.count_of_person = response_data.get('audience_count')
                    pair = Pairs.objects.get(point=point, interest=interest)
                    pair.last_executions = timezone.now()
                    token.is_taken = False
                    token.save()
                    pair.save()
                    entity.save()


async def parser_info(token, pairs):
    result = []
    for pair in pairs:
        point = pair.point
        interest = pair.interest
        token.is_taken = True
        token.save()
        results_qs = Result.objects.filter(coordinate=point, interest=interest).order_by("-end_date")
        if results_qs and (timezone.now() - results_qs[0].end_date).days < 10:
            return
        entity = Result(begin_date=timezone.now())
        sex = 1
        if pair.is_male:
            sex = 2
        criter = {
            "interest_categories": interest.interes_name,
            "geo_near": f"{point.y},{point.x},500",
            "sex": sex,
            "age_from": pair.age_begin,
            "age_to": pair.age_end
        }
        # latitude - широта - y
        # longitude - долгота - x
        json_geo = json.dumps(criter)
        params_dict = {"account_id": token.acc_id, "access_token": token.key, "v": "5.131", "link_url": API_URL,
                       "link_domain": LINK_DOMAIN, "criteria": json_geo}
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, params=params_dict) as response:
                response_json = await response.json()
                try:
                    print(multiprocessing.current_process())
                except Exception:
                    pass
                print(token.key)
                print(response_json)
                await asyncio.sleep(5)
                if response_json.get('error'):
                    if response_json.get('error_code') == 601:
                        token.is_taken = False
                        token.expired = True
                        token.save()
                    else:
                        continue
                else:
                    response_data = response_json.get('response')
                    entity.interest = interest
                    entity.coordinate = point
                    entity.link = API_URL
                    entity.is_male = pair.is_male
                    entity.age_begin = pair.age_begin
                    entity.age_end = pair.age_end
                    entity.count_of_person = response_data.get('audience_count')
                    pair.last_executions = timezone.now()
                    token.is_taken = False
                    token.save()
                    pair.save()
                    entity.save()


def bridge_to_async(corteg):
    asyncio.get_event_loop().run_until_complete(parser(corteg[0], corteg[1]))


def bridge_to_async_info(corteg):
    asyncio.get_event_loop().run_until_complete(parser_info(corteg[0], corteg[1]))


def butch_before_procs():
    num_tokens = ApiKey.objects.filter(expired=False).count()
    date_10_days_ago = timezone.now() - datetime.timedelta(days=10)
    num_points_to_check = Pairs.objects.filter(
        Q(last_executions=None) | Q(last_executions__lte=date_10_days_ago)).count()
    butch_size = int(num_points_to_check / num_tokens + 0.5)
    data = []
    i = 0
    pairs = Pairs.objects.filter(
        Q(last_executions=None) | Q(last_executions__lte=date_10_days_ago))
    for api_key in ApiKey.objects.filter(expired=False):
        data.append((api_key, pairs[i * butch_size: i * butch_size + butch_size]))
        i += 1
    return data


def butch_before_procs_info():
    num_tokens = ApiKey.objects.filter(expired=False).count()
    date_10_days_ago = timezone.now() - datetime.timedelta(days=10)
    num_points_to_check = PairsWithSexAndAge.objects.filter(
        Q(last_executions=None) | Q(last_executions__lte=date_10_days_ago)).count()
    butch_size = int(num_points_to_check / num_tokens + 0.5)
    data = []
    i = 0
    pairs = PairsWithSexAndAge.objects.filter(
        Q(last_executions=None) | Q(last_executions__lte=date_10_days_ago))
    for api_key in ApiKey.objects.filter(expired=False):
        data.append((api_key, pairs[i * butch_size: i * butch_size + butch_size]))
        i += 1
    return data
