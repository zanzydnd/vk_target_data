import asyncio

from django.core.management import BaseCommand

from main.services import async_request_to_api


class Command(BaseCommand):

    def handle(self, *args, **options):
        asyncio.get_event_loop().run_until_complete(async_request_to_api())
