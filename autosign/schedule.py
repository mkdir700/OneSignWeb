from django_celery_beat.models import CrontabSchedule, PeriodicTask


schedule, created = CrontabSchedule.objects.get_or_create(
    minute='1',
    hour='*',
    day_of_week='*',
    day_of_month='*',
    month_of_year='*'
)
