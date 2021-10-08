import os

from django.db import models


class ApiKey(models.Model):
    key = models.CharField(max_length=10000)
    expired = models.BooleanField(default=False)
    acc_id = models.CharField(max_length=255, default=os.environ.get("DEF_ACC_ID"))

    class Meta:
        db_table = "api_keys"
        verbose_name = "Api Ключ"
        verbose_name_plural = "Api Ключи"
