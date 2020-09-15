# project/app/tasks.py


import os
from time import sleep

import celery


from .deployments import create_node


CELERY_BROKER = os.environ.get('CELERY_BROKER')
CELERY_BACKEND = os.environ.get('CELERY_BACKEND')

RABBIT_BROKER = 'amqp://guest@127.0.0.1:5672//'
RABBIT_BACKEND = 'amqp://guest@127.0.0.1:5672//'

app = celery.Celery('tasks', backend=CELERY_BACKEND, broker=CELERY_BROKER)


@app.task
def fib(n):
    sleep(2)  # simulate slow computation
    if n < 0:
        return []
    elif n == 0:
        return [0]
    elif n == 1:
        return [0, 1]
    else:
        results = fib(n - 1)
        results.append(results[-1] + results[-2])
        return results

@app.task
def create():
    return create_node()
