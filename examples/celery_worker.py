from __future__ import absolute_import, unicode_literals
import redis
from celery import Celery
from datetime import timedelta

class CeleryConfig():
    CELERY_BROKER_URL = 'redis://localhost:6379'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379'

    CELERY_BEAT_SCHEDULER = 'celerybeatmongo.MongoPersistentScheduler'
    CELERY_BEAT_SCHEDULE = {
        'add-every-30-seconds': {
            'task': 'myapp.add',
            'schedule': 30.0,
            'args': (16, 16)
        },
        'add-every-90-seconds': {
            'task': 'myapp.add',
            'schedule': timedelta(minutes=1, seconds=30),
            'args': (4, 5)
        }
    }

    CELERY_MONGO_SCHEDULER_URI = 'mongodb://localhost:27017/celerybeatmongo'
    CELERY_MONGO_SCHEDULER_ENTRIES_COL = 'celerybeat_entries'
    CELERY_MONGO_SCHEDULER_META_COL = 'celerybeat_meta'

app = Celery('myapp')
app.config_from_object(CeleryConfig(), namespace='CELERY')

@app.task
def add(x, y):
    return x + y

if __name__ == '__main__':
    app.start(argv=['celery', 'worker', '-B', '-E', '-l', 'DEBUG'])
