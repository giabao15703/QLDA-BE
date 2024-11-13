# python version 3.7.4

venv/bin/activate: requirements.txt
	python -m venv venv
	pip install -r requirements.txt

run: venv/bin/activate
	python project/manage.py runserver

venv\Scripts\Activate.ps1: requirements.txt
	python -m venv venv
	pip install -r requirements.txt

run-window: venv\Scripts\Activate.ps1
	python project/manage.py runserver

run-only:
	python project/manage.py runserver

migrate:
	python project/manage.py migrate

makemigrations:
	python project/manage.py makemigrations

showmigrations:
	python project/manage.py showmigrations

# example: make my_app=master_data version=0016 revertmigrations
# revert migration of master_data to version 0017
# check apps and version using: make showmigrations
revertmigrations:
	python project/manage.py migrate $(my_app) $(version)

# example: make appname=master_data newapp
newapp:
	python project/manage.py startapp ${appname}
