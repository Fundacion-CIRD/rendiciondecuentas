# Plataforma de transparencia de donaciones

Este es un proyecto del [CIRD](https://cird.org.py) en colaboración con [CIVILAB](https://civilab.org.py).

Entre las funionalidades principales de la plataforma tenemos:

- Administración de donaciones recibidas
- Administración de gastos
- Listado de donaciones recibidas y compras con filtros de montos, fechas y donante.
- Detalle de compras: Items adquiridos y documentos relacionados
- Descarga en CSV y JSON de donaciones  y compras
 

## Requirements
  - [Python >= 3.6](https://www.python.org/)
  - [Pipenv](https://github.com/pypa/pipenv)
  - [PostgreSQL](https://www.postgresql.org/)
  - [NodeJS](https://nodejs.org)

## Development
1. Clone repository: `git clone xxxxxx`
2. Install dependencies: `pipenv install`
3. Create a file called `secrets.json` in root directory
4. Insert the following lines into the file:
    ````
   {
      "allowed_hosts": ["localhost", "127.0.0.1", <ANY_OTHER_HOST>],
      "db_name": "<DB_NAME>",
      "db_user": "<POSTGRESQL_DB_USER>",
      "db_password": "<POSTGRESQL_DB_PASSWORD>",
      "db_host": "<POSTGRESQL_DB_HOST>",
      "db_port": "<POSTGRESQL_DB_PORT>",
      "secret_key": "<DJANGO_SECRET_KEY>",
      "debug": "TRUE"
    }
5. Activate virtualenv: `pipenv shell`
6. Run migrations: `python manage.py migrate`
7. Install `unaccent` extension on your PostgreSQL database:
    ````
   $ psql -d <DB_NAME>
   <DB_NAME>=# create extension unaccent;
8. Create SuperUser: `python manage.py createsuperuser`
9. Go to `static_src`
10. Run `npm install`
11. Run `npm run compile:css:watch`
8. Run Development Server: `python manage.py runserver`
9. Go to localhost:8000/admin and  create the first instances of donations and adquisitions. 
10. Go to localhost:8000/


## Contribuye!

Estamos abiertos a recibir bugs, mejoras  y correcciones en la documentación.

Podes hacer en la seccion  de issues [github issue tracker](http://github.com/xxx).



## Licencia

Este software esta liberado bajo la licencia  GPL V2.
