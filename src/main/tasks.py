import logging

from main.models.in_house import ApiKey
from target_data.celery import app

logger = logging.getLogger(__name__)


@app.task
def get_data_vk_api():
    token = ApiKey.objects.filter(is_taken=False)[0]



@app.task
def update_api_keys():
    pass


@app.task
def check_old_ones():
    pass
