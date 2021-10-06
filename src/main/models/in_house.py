from django.db import models


class ApiKeys(models.Model):
    key = models.CharField(max_length=10000)
    is_taken = models.BooleanField(default=False)

    class Meta:
        db_table = "api_keys"
        verbose_name = "Api Ключ"
        verbose_name_plural = "Api Ключи"
