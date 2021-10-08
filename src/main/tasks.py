import logging

from main.models import InterestCategory, Coord
from main.models.in_house import ApiKey
from main.services import make_request_to_api
from target_data.celery import app

logger = logging.getLogger(__name__)


@app.task
def get_data_vk_api():
    interests = InterestCategory.objects.all()
    points = Coord.objects.all()
    for interest in interests:
        for point in points:
            make_request_to_api(interest, point, try_num=1, err_cnt=0)
