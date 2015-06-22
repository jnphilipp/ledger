### Install
* Download source
* Create virtual enviroment and activate it

  ```
  $ virtualenv -p /usr/bin/python3 venv
  $ source venv/bin/activate
  ```
* Create file TIMA/settings.ini with the folloing configurations, for details
  see [https://docs.djangoproject.com/en/1.8/ref/settings/](https://docs.djangoproject.com/en/1.8/ref/settings/)

  ```
  [secrets]
  SECRET_KEY: str
  SESSION_COOKIE_SECURE: bool
  CSRF_COOKIE_SECURE: bool
  SESSION_EXPIRE_AT_BROWSER_CLOSE: bool

  [database]
  DATABASE_ENGINE: django.db.backends.sqlite3
  DATABASE_NAME: db.sqlite3
  DATABASE_USER: str
  DATABASE_PASSWORD: str
  DATABASE_HOST: str
  DATABASE_PORT: int

  [debug]
  DEBUG: bol
  TEMPLATE_DEBUG: bool

  [host_email]
  DEFAULT_FROM_EMAIL: str
  SERVER_EMAIL: str
  EMAIL_USE_TLS: bool
  EMAIL_USE_SSL: bool
  EMAIL_HOST: jnphilipp.org
  EMAIL_PORT: int
  EMAIL_HOST_USER: bool
  EMAIL_HOST_PASSWORD: bool

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
  $ python manage.py syncdb
  ```
* Collect static files (only necessary for production)

  ```
  $ python manage.py collectstatic
  ```