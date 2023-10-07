from django.core.management import BaseCommand

from django_celery_beat.models import CrontabSchedule, PeriodicTask

from mailing.settings import TIME_ZONE


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '-r', '--run', action='store_true',
            help='Запуск периодической задачи для отправки ежедневного отчета'
        )
        parser.add_argument(
            '-s', '--stop', action='store_true',
            help='Остановка периодической '
            'задачи для отправки ежедневного отчета'
        )

    def handle(self, *args, **kwargs):
        run = kwargs['run']
        # stop = kwargs['stop']
        task_name = 'send_report_task'

        if run:
            schedule, _ = CrontabSchedule.objects.get_or_create(
                minute=57, hour=10, day_of_week='*', timezone=TIME_ZONE)
            task, _ = PeriodicTask.objects.get_or_create(
                name=task_name,
                task='api.tasks.send_report_task',
                crontab=schedule)
            task.enabled = True
            task.save()
            print('Задача запущенна')
        else:
            task = PeriodicTask.objects.get(name=task_name)
            task.enabled = False
            task.save()
            print('Задача остановлена')
