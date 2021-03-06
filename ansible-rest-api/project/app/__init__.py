# project/app/__init__.py


import json

import falcon
from celery.result import AsyncResult

from app.tasks import fib, create


class Ping(object):
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.body = json.dumps('pong!')


class CreateNode(object):

    def on_post(self, req, resp):
        raw_json = req.stream.read()
        result = json.loads(raw_json, encoding='utf-8')
        task = create.delay()
        resp.status = falcon.HTTP_200
        result = {
            'status': 'success',
            'data': {
                'task_id': task.id
            }
        }
        resp.body = json.dumps(result)


class NodeStatus(object):

    def on_get(self, req, resp, task_id):
        task_result = AsyncResult(task_id)
        result = {'status': task_result.status, 'result': task_result.result}
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(result)


app = falcon.API()

app.add_route('/ping', Ping())
app.add_route('/create', CreateNode())
app.add_route('/status/{task_id}', NodeStatus())
