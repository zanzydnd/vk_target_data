from django.core.management import BaseCommand

from main.models import InterestCategory, Coord, Pairs


class Command(BaseCommand):
    def handle(self, *args, **options):
        data = []
        for interest in InterestCategory.objects.all():
            for coord in Coord.objects.all():
                data.append(Pairs(interest=interest, point=coord))
                if len(data) >= 50000:
                    Pairs.objects.bulk_create(data, ignore_conflicts=True)
                    data.clear()
        if data:
            Pairs.objects.bulk_create(data, ignore_conflicts=True)
