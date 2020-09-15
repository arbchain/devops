# Rest API to run ansible playbooks

REST API with background process handling using Falcon, Celery, and Docker

### Quick Start

Spin up the containers:

```sh
$ docker-compose up -d
```

Open your browser to http://localhost:8000/ping to view the app or to http://localhost:5555 to view the Flower dashboard.

Trigger a new task:

```sh
$ curl -X POST http://localhost:8000/create
```

Check the status:

```sh
$ curl http://localhost:8000/status/<ADD_TASK_ID>
```

### Credits

Reference [post](https://testdriven.io/asynchronous-tasks-with-falcon-and-celery).
