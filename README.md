# zignative-app

## In project folder create virtual environment for project:

`pip install virtualenv
`
<br> <br>
`virtualenv venv 
`

In order to run a project-related command, venv must always be active first.

#### Deactivate venv:

`deactivate
`
## Declare the settings in venv (Windows):

_Open venv\Scripts\activate.bat file_

_Add the following line to the end of the file;_

`set "DJANGO_SETTINGS_MODULE=zignative.settings.development"
`
# Activate virtual environment:

`
.\venv\Scripts\activate
`
# Install dependecies:

`pip install -r requirements.txt
`
# Make Migrations:

`python manage.py makemigrations
` <br><br>
`python manage.py migrate
`


# Run:

`python manage.py runserver
`
# Create Superuser

`python manage.py createsuperuser`

#### !!! After creating a superuser, specify the role of the user from the admin panel before logging in to the site. otherwise you will get error !!!

<hr>



# For payment transactions

"Stripe CLI" must be running from the backend while the project is running in order for the payment to be processed.

-Install Stripe CLI

https://github.com/stripe/stripe-cli

Go to the folder where stripe.exe is located

### Login Stripe:

`.\stripe.exe login`

### After login, activate stripe cli:

`.\stripe.exe listen --forward-to localhost:8000/webhooks/stripe/`

You should see an output like this:

> Ready! Your webhook signing secret is whsec_123123123123 (^C to quit)

Copy and past this secret key to `STRIPE_WEBHOOK_SECRET` variable in `zignative/settings/development.py`


<hr>

# Mail System

All mail operations within the application are handled by asynchronous background tasks.

### Install Erlang Language for RabbitMQ

https://www.erlang.org/downloads

### Install RabbitMQ for message broker:

https://www.rabbitmq.com/download.html


### In order to perform mail operations, the following command should be run in another console in the project directory:

`celery -A zignative worker --loglevel=info -P eventlet`



