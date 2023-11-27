# tsoha-opetussovellus
The current functionality of the app is as follows:
- Users can create a student or a teacher account, which have different functionalities
- Students can view all courses, join them, leave them, view text materials do exercises
- Teachers can create courses, add exercises and text materials, delete exercises and delete courses
- Exercises can be essay exercises or multiple choice exercises: Essay exercises upon submission are always correct, and the example answer is shown, while multiple choice questions can be correct or wrong
- When viewing a course, students can see which exercises they have done and which they haven't, along with if they are correct or incorrect
- Teachers can see which students have done which exercises, and if they are correct or incorrect

# Running the app
**With Docker** <br />
<br />
First, clone the repository:
```
$ git clone https://github.com/candyliaa/tsoha-opetussovellus.git
```
You can run the app with [Docker](https://www.docker.com/). You can install it [here](https://docs.docker.com/get-docker/).
The structure of the Docker containers follows [this](https://docs.docker.com/compose/gettingstarted/) guide.
To run the app yourself, generate a secret key: 
```
$ python3
>>> import secrets
>>> secrets.token_hex(16)
```
and replace `KEY GOES HERE` in `compose.yaml.example` with the key you just generated. Then rename `compose.yaml.example` to just `compose.yaml`.
After that, launch the Docker Desktop application, and run
```
$ docker compose up
```
You can then open the app at [`http://localhost:8000`](http://localhost:8000) . <br />
<br />
**Without Docker**

Alternatively, the app can be ran without Docker.
Clone the repository:
```
$ git clone https://github.com/candyliaa/tsoha-opetussovellus.git
```
Remove all Docker related files: `Dockerfile` in both the `app` and `db` dictionaries, as well as `compose.yaml.example`.
Then, create a `.env` file, and add two lines, one for the `SECRET_KEY`, and one for the `DATABASE_URL`. It should look like this:
```
SECRET_KEY = <KEY_GOES_HERE>
DATABASE_URL = <URL_GOES_HERE>
```
Generate a secret key:
```
$ python3
>>> import secrets
>>> secrets.token_hex(16)
```
As for the `DATABASE_URL`, you can input the following: `"postgresql://postgres@localhost/postgres"`. 
Be mindful of the fact that this attempts to connect to a local database named `postgres`, which might already exist.

Next, install all required packages with a virtual environment:
```
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r ./app/requirements.txt
```
Then, build the database using the schema:
```
$ psql < db/schema.sql
```
Optionally, you can also add some test data to the database:
```
$ psql < db/test_data.sql
```
You can now run the app with the command
```
$ flask run
```

# Current state of the app
Although the app is mostly done functionality wise, the styling of the web pages is still to be improved. Some of the code in `routes.py` has been moved to `data.py` so that the logic in `routes.py` is easier to follow. The code has also been formatted using pylint and Black Formatter.
There should be no security vulnerabilities (at least no SQL injection, XSS or CSRF attack risk). 
