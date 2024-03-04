## Pre Requirements
  - python 3.9.6

## Install

  - python -m venv /path/to/new/virtual/environment
  - pip install -r requirments.txt
  - pip install -r requirments_dev.txt [only for local env]
  - pip install pre-commit [only for local env]

## Run
  ### Local
    - python manage.py migrate
    - python manage.py runserver
    
       `to send email run the celery`
    - celery -A user_login worker --loglevel=info
   ### For Docker users
    - pre-requirement: Docker
    - docker compose up --build


## Images
<img width="798" alt="google ana" src="https://github.com/melih-karakoc/user_login/assets/53266188/d1a201f5-f51b-480a-ab02-11221280c0f1">
<img width="757" alt="signup" src="https://github.com/melih-karakoc/user_login/assets/53266188/a86a7a13-6880-4eb4-8702-5d668c77b5aa">
<img width="645" alt="home" src="https://github.com/melih-karakoc/user_login/assets/53266188/d1ed6f98-19d9-477d-b8ec-d0f32ad6ae38">
