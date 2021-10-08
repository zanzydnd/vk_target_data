from django.db import models


class InterestCategory(models.Model):
    interes_name = models.CharField(max_length=200, unique=True)

    class Meta:
        db_table = "interest_category"
        verbose_name = "Интерес"
        verbose_name_plural = "Интересы"


class Coord(models.Model):
    x = models.DecimalField(max_digits=30, decimal_places=15)
    y = models.DecimalField(max_digits=30, decimal_places=15)

    class Meta:
        unique_together = ['x', 'y']
        db_table = "coordinate"
        verbose_name = "Координата"
        verbose_name_plural = "Координаты"


class Result(models.Model):
    coordinate = models.ForeignKey(Coord, on_delete=models.SET_NULL, null=True, related_name="results")
    interest = models.ForeignKey(InterestCategory, on_delete=models.SET_NULL, null=True, related_name="results")
    link = models.TextField(max_length=100000)
    count_of_person = models.BigIntegerField(default=0)
    begin_date = models.DateTimeField()
    end_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "result"
        verbose_name = "Результат"
        verbose_name_plural = "Результаты"
