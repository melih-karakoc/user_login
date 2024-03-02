## Install

  - python -m venv /path/to/new/virtual/environment
  - pip install -r requirments.txt

## Run on local
  - python manage.py migrate
  - python manage.py runserver
    
     `to send email run celery`
  - celery -A user_login worker --loglevel=info
