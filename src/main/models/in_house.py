import os

from django.db import models

from main.models import InterestCategory, Coord


class ApiKey(models.Model):
    key = models.CharField(max_length=10000)
    expired = models.BooleanField(default=False)
    acc_id = models.CharField(max_length=255, default=os.environ.get("DEF_ACC_ID"))
    is_taken = models.BooleanField(default=False)

    class Meta:
        db_table = "api_keys"
        verbose_name = "Api Ключ"
        verbose_name_plural = "Api Ключи"


class Pairs(models.Model):
    interest = models.ForeignKey(InterestCategory, on_delete=models.CASCADE)
    point = models.ForeignKey(Coord, on_delete=models.CASCADE)
    last_executions = models.DateTimeField(null=True)

    class Meta:
        db_table = "pairs"
        unique_together = ['interest', 'point']


#class BatchesForPairs(models.Model):
#    from_ = models.IntegerField(default=0)
#    to_ = models.IntegerField()
#    api_key = models.ForeignKey(ApiKey, on_delete=models.CASCADE)
#
#    class Meta:
#        db_table = "batch"
