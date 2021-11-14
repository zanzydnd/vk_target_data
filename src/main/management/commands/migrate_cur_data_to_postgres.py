import asyncio
from multiprocessing import Pool

import django

django.setup()
from django.core.management import BaseCommand
from django.utils import timezone

from main.models import InterestCategory, Result, Coord


class Command(BaseCommand):

    def handle(self, *args, **options):
        num_procs = 5

        data = []

        count = Result.objects.using('default').filter(is_male__isnull=False, age_begin__isnull=False,
                                                       age_end__isnull=False, count_of_person__gt=0).count()

        butch_size = int(count / num_procs + 0.5)

        data = []

        for i in range(5):
            data.append((i * butch_size, i * butch_size + butch_size))

        with Pool(num_procs) as p:
            p.map(bridge_to_async, data)


def bridge_to_async(data):
    asyncio.get_event_loop().run_until_complete(worker(data))


async def worker(sizes):
    i = sizes[0]
    while i <= sizes[1]:
        data = Result.objects.using('default').filter(is_male__isnull=False, age_begin__isnull=False,
                                                      age_end__isnull=False, count_of_person__gt=0)[i: i + 1000]
        for result in data:
            interest = InterestCategory.objects.using('cache').get(id=result.interest.id)
            coordinate = Coord.objects.using('cache').get(x=result.coordinate.x, y=result.coordinate.y)

            save = Result(interest=interest, coordinate=coordinate, count_of_person=result.count_of_person,
                          begin_date=timezone.now(), end_date=timezone.now(), age_begin=result.age_begin,
                          age_end=result.age_end, is_male=result.is_male, link=result.link)

            save.save(using='cache')
            print('saved')
        del data
        i += 1000

