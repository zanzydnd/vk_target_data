from django.core.management import BaseCommand

from main.models import InterestCategory, Coord, PairsWithSexAndAge


class Command(BaseCommand):
    def handle(self, *args, **options):
        data = []
        AGES = [(14, 18), (18, 21), (21, 24),
                (24, 27), (27, 30), (30, 35), (35, 45), (45, 54), (54, 65), (65, 80)]
        for interest in InterestCategory.objects.using("cache").all():
            for coord in Coord.objects.using("cache").all():
                for age in AGES:
                    data.append(PairsWithSexAndAge(interest=interest, point=coord, age_begin=age[0], age_end=age[1],
                                                   is_male=True))
                    data.append(PairsWithSexAndAge(interest=interest, point=coord, age_begin=age[0], age_end=age[1],
                                                   is_male=False))
                if len(data) >= 50000:
                    PairsWithSexAndAge.objects.using("cache").bulk_create(data, ignore_conflicts=True)
                    data.clear()
        if data:
            PairsWithSexAndAge.objects.using("cache").bulk_create(data, ignore_conflicts=True)
