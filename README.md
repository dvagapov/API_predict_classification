## Use docker-compose

go to project folder and then:
	$ docker-compose up
	
Will run four containers:
	api  - python Flask API
	postgres  - DB postgreSQL 

For postgres will also execute pgconfig/init_db.sql. The script contains Schema of DB recommendation with small sample data. 

## Used libs for API:
	* json
	* sys, os, io, base64

	[requirements.txt]
	* werkzeug==0.16.0 
	* Flask==1.1.1
	* Flask-HTTPAuth==3.3.0
	* Flask_restx==0.1.1
	* psycopg2-binary==2.8.4
	* numpy
	* pandas
	* scikit-learn

----- Manual run without docker-compose
## For developing API
### Before
Create and activate virtual environment with python 3.6+

	* If "virtualenv" not istalled before:
		$ python3 -m pip install --user virtualenv

	* In main folder run below commands:
		$ python3 -m venv api
		$ cd api/
		$ source bin/activate
	
Install the requirements
	$ pip install -r requirements.txt

Run Flask RESTful
	$ export FLASK_APP=project/__init__.py
	$ export PG_HOST=127.0.0.1
	$ export PG_DB=postgres
	$ export PG_USER=api_user
	$ export PG_PASS=api$pass
	$ python manage.py run

### Usage API service
	#### Test page "/ping"
	$ curl http://localhost:5000/ping
		output: {"status": "success  ", "message": "pong!"}
	
	#### Default token auth (stored into Database)
	-H 'Authorization: Token tokenTest1'
	
	#### page "/classify"
	$ curl http://localhost:5000/classify -H 'Authorization: Token tokenTest1'
		output: { "predicted_class": "1.0", "status": "OK"}
	#### page "/stats"
	$ curl http://localhost:5000/stats -H 'Authorization: Token tokenTest1'
        output: {"mean_f1": 0.25, "mean_f2": 0.33, "most_frequent_f3": "A"}

### Stop API service
For deactivate virtual environment just type:
	$ deactivate