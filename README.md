## Run below commands to setup project.

Install postgres: https://www.postgresql.org/download/

git clone https://github.com/ARSPACE-LTD/arspace-backend.git

cd arspace

mv env.example .env

Change these info to your postgres db informations in .env file:

DB_NAME="arspace"
DB_USERNAME="postgres"
DB_PASSWORD="postgres"

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt

python manage.py createsuperuser

python manage.py runserver

And navigate to `http://127.0.0.1:8000/admin/login`

https://arspace.website/admin/login?next=/admin/dashboard
