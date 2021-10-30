import datetime
import logging

from django.db.models import Q
from django.utils import timezone

from main.models.in_house import Pairs
from target_data.celery import app

logger = logging.getLogger(__name__)


@app.task
def get_data_vk_api():
    flag = True
    while flag:
        date_10_days_ago = timezone.now() - datetime.timedelta(days=10)
        try:
            pair = Pairs.objects.filter(Q(last_executions=None) | Q(last_executions__lte=date_10_days_ago))[0]
        except Exception:
            flag = False
        if not pair:
            flag = False
        else:
            pass
            #make_request_to_api(pair.interest, pair.point, try_num=1, err_cnt=0)
    # for pair in Pairs.objects.filter(Q(last_executions=None)|Q(last_executions__lte=date_10_days_ago)):
    #    make_request_to_api(pair.interest, pair.point, try_num=1, err_cnt=0)
