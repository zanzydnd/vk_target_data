from django.db import models


class InterestCategory(models.Model):
    interes_name = models.CharField(max_length=1000, unique=True)

    class Meta:
        db_table = "interest_category"
        verbose_name = "Интерес"
        verbose_name_plural = "Интересы"


class Coord(models.Model):
    x = models.IntegerField()
    y = models.IntegerField()

    class Meta:
        unique_together = ['x', 'y']
        db_table = "coordinate"
        verbose_name = "Координата"
        verbose_name_plural = "Координаты"

# !Это не нужно можно просто по полям результата смотреть.
class RequestsCoordInterestCombination(models.Model):
    coord = models.ForeignKey(Coord, on_delete=models.CASCADE, related_name="executed_interest")
    interest = models.ForeignKey(InterestCategory, on_delete=models.CASCADE, related_name="executed_coord")

    class Meta:
        unique_together = ['coord', 'interest']
        db_table = "request_comb_interest_coord"
        verbose_name = "Использованное сочетание coord + interest"
        verbose_name_plural = "Использованные сочетания coord + interest"


class Result(models.Model):
    coordinate = models.ForeignKey(Coord, on_delete=models.SET_NULL, related_name="results")
    interest = models.ForeignKey(InterestCategory, on_delete=models.SET_NULL, related_name="results")
    link = models.CharField(max_length=100000)
    count_of_person = models.BigIntegerField(default=0)
    begin_date = models.DateTimeField(auto_now=True)
    end_date = models.DateTimeField()

    class Meta:
        db_table = "result"
        verbose_name = "Результат"
        verbose_name_plural = "Результаты"


class FailedResult(Result):
    is_fixed = models.BooleanField(default=False)
    error_msg = models.CharField(max_length=100000, default="Error")
    error_code = models.IntegerField(null=True)
    last_fix_try_date = models.DateTimeField()

    class Meta:
        db_table = "failed_result"
        verbose_name = "Не полученный результат"
        verbose_name_plural = "Не полученные результаты"
