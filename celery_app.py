from celery import Celery
from celery.schedules import crontab

celery = Celery('crud_app', broker='redis://localhost:6379', backend='redis://localhost:6379', include=['core.tasks'])

celery.conf.timezone = 'Asia/Kolkata'

celery.conf.beat_schedule = {
        'celery_beat_task': {
            'task': 'celery_beat_task',
            'schedule': crontab(minute="*/1")      # every minute
        },
}