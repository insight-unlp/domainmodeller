#! /bin/sh

celery worker -E -Q celery --config=domainmodeller.celeryconfig --loglevel=INFO --logfile=logs/celery.log

