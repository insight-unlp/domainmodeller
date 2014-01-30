BROKER_URL = 'amqp://localhost:5672//'
CELERY_RESULT_BACKEND = 'amqp://'
CELERY_IMPORTS = ('domainmodeller.celerytasks.celery_tasks', )
CELERY_TASK_PUBLISH_RETRY = True
CELERYD_PREFETCH_MULTIPLIER = 10
