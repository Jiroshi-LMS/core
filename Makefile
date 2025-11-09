run:
	python3 manage.py runserver 8001

noreload:
	python3 manage.py runserver 8001 --noreload

run-tasks:
	celery -A dashboard worker -l info