## Run below commands to setup project.

git clone https://github.com/devgeektech/arspace.git

cd arspace

mv env.example .env

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt

python manage.py createsuperuser

python manage.py runserver

And navigate to `http://127.0.0.1:8000/admin/login`