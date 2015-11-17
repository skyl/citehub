# citehub
Gather citations into yur database with python.

Based on django-publications and scholar.py, this app lets you browse scholar from the command line and save citations into Django models. You can also use the admin, the django-publications template frontend or the json API (TODO) for various CRUD.

Install
-------

With Python3 already installed.

Install the dependencies:
```
pip install -r requirements.txt
```

Initialize the database:
```
./manage.py migrate
```

Start the server:
```
./manage.py runserver
```

Query Scholar with the command line interface:
```
./manage.py search term1 term2
```

