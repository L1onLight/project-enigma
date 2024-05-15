SHELL := /bin/bash

init:
	cp .env.sample .env && python3 -m venv .venv && source ./.venv/bin/activate && pip install -r requirements.txt && python3 manage.py migrate && python3 manage.py runserver
run:
	python3 manage.py runserver