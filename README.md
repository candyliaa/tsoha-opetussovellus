# tsoha-opetussovellus
The current functionality of the app is as follows:
- Users can create a student or a teacher account, which have different functionalities
- Students can view all courses, join them, leave them, view text materials do exercises
- Teachers can create courses, add exercises and text materials, delete exercises and delete courses
- Exercises can be essay exercises or multiple choice exercises: Essay exercises upon submission are always correct, and the example answer is shown, while multiple choice questions can be correct or wrong
- When viewing a course, students can see which exercises they have done and which they haven't, along with if they are correct or incorrect
- Teachers can see which students have done which exercises, and if they are correct or incorrect

# Running the app
First, clone the repository:
```
git clone https://github.com/candyliaa/tsoha-opetussovellus
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
You can then open the app at `http://localhost:8000` .

# Current state of the app
Although the app is mostly done functionality wise, the styling is still to be improved - both the look of the HTML pages, and the structure of the code (mostly moving things such as SQL -queries from the routes in `routes.py` to another file, for easier reading of routes.)

There are also some potential bugs with displaying exercises and courses properly when there are multiple students in a course.
Right now there is one such bug I'm aware of: if two students join the same course, and one of them does any exercise, that exercise doesn't show up for the other student. 

More validation checks for data submitted through forms need to be implemented, too - mainly getting rid of CSRF-vulnerabilities.
