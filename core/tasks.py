from celery_app import celery as app

from celery import shared_task

@app.task
def add(x, y):
    print(x,y,'wdlsakdlw')
    print(x+y)

@shared_task(name="celery_beat_task")
def celery_beat_task():
    print("celery beat demo")
    return