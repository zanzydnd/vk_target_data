import django
from django.core.management import BaseCommand

django.setup()

from multiprocessing import Pool
from main.models import ApiKey
from main.services import butch_before_procs, bridge_to_async



class Command(BaseCommand):
    def handle(self, *args, **options):

        num_tokens = ApiKey.objects.filter(expired=False).count()

        arrays = butch_before_procs()

        with Pool(num_tokens) as p:
            p.map(bridge_to_async, arrays)
