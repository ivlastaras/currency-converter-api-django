# Disclaimer

This is a project in order to experiment with the Django framework.

# How to run

You need python 3.9.7 to run this application.

You should create a virtual environment using:

```shell
python -m venv .venv
```
and then activate it using:
```shell
source .venv/bin/activate
```

After that you need to install the necessary requirements using:

```shell
pip install -r requirements.txt
```

You should execute the following commands inside the yellow folder:

```shell
python manage.py migrate
python manage.py runserver
```

You can use the application through Swagger which is located at the following endpoint `http://localhost:8000/swagger/`

To login through swagger you should use "Authenticate" and then type in "Bearer " ("Bearer" + SPACE) and then fill in the access token that was provided from the login process.

You can get the exchange rates with a specific target in either json or xml format through the right field in swagger that says 
"Response Content Type:application/json"


# How to test

To run the tests run:

```shell
python manage.py test core.tests
```

To run the test for User Registration run:

```shell
python manage.py test core.tests.UserRegisterTests
```

To run the test for User Login run:

```shell
python manage.py test core.tests.UserLoginTests
```

To run the test for `http://localhost:8000/rates/`

```shell
python manage.py test core.tests.RatesTests
```

To run the test for `http://localhost:8000/rates/{base currency}`

```shell
python manage.py test core.tests.RatesWithBaseTests
```

To run the test for `http://localhost:8000/rates/{base currency}/{target currency}`

```shell
python manage.py test core.tests.RatesWithBaseAndTargetTests
```

To run the test for `http://localhost:8000/seed/`

```shell
python manage.py test core.tests.SeedTest
```
