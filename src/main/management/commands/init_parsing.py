import datetime
import logging

from django.db.models import Q
from django.utils import timezone

from main.models.in_house import Pairs
from main.services import make_request_to_api
from django.core.management import BaseCommand


class Command(BaseCommand):
    date_10_days_ago = timezone.now() - datetime.timedelta(days=10)
    for pair in Pairs.objects.filter(Q(last_executions=None) | Q(last_executions__lte=date_10_days_ago)):
        make_request_to_api(pair.interest, pair.point, try_num=1, err_cnt=0)