### Install
* Download source
* Create virtual enviroment and activate it

  ```
  $ virtualenv -p /usr/bin/python3 .venv
  $ source .venv/bin/activate
  ```
* Create file ledger/settings.ini with the folloing configurations, for details
  see [https://docs.djangoproject.com/en/1.10/ref/settings/](https://docs.djangoproject.com/en/1.10/ref/settings/)

  ```
  [database]
  DATABASE_ENGINE: django.db.backends.sqlite3
  DATABASE_NAME: db.sqlite3
  DATABASE_USER: str
  DATABASE_PASSWORD: str
  DATABASE_HOST: str
  DATABASE_PORT: int


  [debug]
  DEBUG: bool
  TEMPLATE_DEBUG: bool


  [i18n]
  LANGUAGE_CODE: en-us
  TIME_ZONE: UTC
  USE_I18N: bool
  USE_L10N: bool
  USE_TZ: bool


  [secrets]
  SECRET_KEY:
  SESSION_COOKIE_SECURE: false
  CSRF_COOKIE_SECURE: false
  SESSION_EXPIRE_AT_BROWSER_CLOSE: false


  [host_email]
  DEFAULT_FROM_EMAIL: str
  SERVER_EMAIL: str
  EMAIL_USE_TLS: bool
  EMAIL_USE_SSL: bool
  EMAIL_HOST: str
  EMAIL_PORT: int
  EMAIL_HOST_USER: str
  EMAIL_HOST_PASSWORD: str


  [admins]
  str(name): str(email)


  [host]
  ALLOWED_HOSTS: str,str
  ```
* Install requirements

  ```
  $ pip install -r requirements
  ```
* Migrate database and create superuser

  ```
  $ python manage.py migrate
  $ python manage.py createsuperuser
  ```
* Collect static files (only necessary for production)

  ```
  $ python manage.py collectstatic
  ```
