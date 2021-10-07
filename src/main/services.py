from main.models import Result


def get_points_by_interest_name_service(interest_name: str):
    return Result.objects.filter(interest__interes_name=interest_name, count_of_person__gt=0).select_related(
        'coordinate')
