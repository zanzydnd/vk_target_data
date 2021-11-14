import django

django.setup()

import asyncio
import datetime
import json
import multiprocessing

import aiohttp
from django.db.models import Q
from django.utils import timezone
from main.models import Result, InterestCategory, Coord
from main.models.in_house import ApiKey, Pairs, PairsWithSexAndAge
from django.db.models import Sum


def pick_points(interest_name: str, sex: str, age: str):
    interest = InterestCategory.objects.using("cache").get(interes_name=interest_name)

    if sex == "-":
        sex = None
    elif sex == "м":
        sex = True
    else:
        sex = False

    if age == "-":
        age = None

    query = Q(interest=interest)

    if sex:
        query &= Q(is_male=sex)
    else:
        query &= Q(is_male__isnull=False)

    if age:
        from_, to_ = list(map(int, age.split("-")))
        query &= Q(age_begin=from_, age_end=to_)
    else:
        query &= Q(age_begin__isnull=False, age_end__isnull=True)

    points = Result.objects.using("cache").filter(query).values('coordinate') \
        .annotate(count_of_person=Sum('count_of_person'))

    print(points)
    print(points[0], points[1])

    return points


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
        # response = requests.post(API_URL, params=params_dict, headers={"User_Agent": generate_user_agent()})
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


async def parser_info(token, pairs_limit):
    i = pairs_limit[0] + 1000
    date_10_days_ago = timezone.now() - datetime.timedelta(days=10)
    while i <= pairs_limit[1]:
        pairs = PairsWithSexAndAge.objects.filter(
            Q(last_executions=None) | Q(last_executions__lte=date_10_days_ago))[i - 1000:i]
        for pair in pairs:
            point = pair.point
            interest = pair.interest
            token.is_taken = True
            token.save()
            results_qs = Result.objects.filter(coordinate=point, interest=interest, is_male=pair.is_male,
                                               age_begin=pair.age_begin, age_end=pair.age_end).order_by("-end_date")
            if results_qs and (timezone.now() - results_qs[0].end_date).days < 10:
                continue
            entity = Result(begin_date=timezone.now())
            sex = 1
            if pair.is_male:
                sex = 2
            print(str(interest.interes_name))
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
                        try:
                            interest_from_chache = InterestCategory.objects.using('cache').get(
                                id=interest.id)
                            coordinate_from_cache = Coord.objects.using('cache').get(x=point.x, y=point.y)

                            response_data = response_json.get('response')
                            entity.interest = interest
                            entity.coordinate = point
                            entity.link = API_URL
                            entity.is_male = pair.is_male
                            entity.age_begin = pair.age_begin
                            entity.age_end = pair.age_end
                            entity.count_of_person = int(response_data.get('audience_count'))
                            pair.last_executions = timezone.now()

                            try:
                                update_cache = Result.objects.using('cache').get(interest=interest_from_chache,
                                                                                 coordinate=coordinate_from_cache,
                                                                                 is_male=pair.is_male,
                                                                                 age_begin=pair.age_begin,
                                                                                 age_end=pair.age_end)
                                update_cache.end_date = timezone.now()
                                update_cache.count_of_person = int(response_data.get('audience_count'))
                                update_cache.save(using='cache')
                                print('updated in cache')
                            except Exception as e:
                                entity_to_cache = Result(begin_date=timezone.now())
                                entity_to_cache.interest = interest_from_chache
                                entity_to_cache.coordinate = coordinate_from_cache
                                entity_to_cache.link = API_URL
                                entity_to_cache.is_male = pair.is_male
                                entity_to_cache.age_begin = pair.age_begin
                                entity_to_cache.age_end = pair.age_end
                                entity_to_cache.count_of_person = int(response_data.get('audience_count'))
                                entity_to_cache.save(using='cache')
                                print(e)
                            token.is_taken = False
                            token.save()
                            pair.save()
                            entity.save(using='default')
                            print('saved default')
                        except Exception as e:
                            print(e)
        del pairs
        i += 1000


def bridge_to_async(corteg):
    asyncio.get_event_loop().run_until_complete(parser(corteg[0], corteg[1]))


def bridge_to_async_info(corteg):
    print("async bridge")
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
    # pairs = PairsWithSexAndAge.objects.filter(
    #    Q(last_executions=None) | Q(last_executions__lte=date_10_days_ago))
    for api_key in ApiKey.objects.filter(expired=False):
        data.append((api_key, (i * butch_size, i * butch_size + butch_size)))
        i += 1
    return data

