import os

from django.core.management import BaseCommand
import vk_api

from main.models import InterestCategory


class Command(BaseCommand):
    def handle(self, *args, **options):
        session = vk_api.VkApi(token=os.environ.get("API_KEY"))

        vk = session.get_api()

        interes = session.method("ads.getSuggestions", {"section": "interest_categories_v2", "country": 1})
        data = list(InterestCategory(interes_name=interes[i]['name']) for i in range(len(interes)))
        InterestCategory.objects.bulk_create(data)
