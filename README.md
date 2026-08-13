# To-Do CRUD API (Python / FastAPI + SQLite)

A To-Do list API built with **FastAPI**, supporting full CRUD (Create, Read, Update, Delete) operations. Data is now persisted in a **SQLite** database instead of an in-memory list — restarting the server no longer wipes your tasks. Built as part of the FlyRank Backend AI Engineering internship (Week 2–3 assignments).

## What this is

This API lets you manage a list of tasks — create new tasks, view them, update their title/status, and delete them. The API itself hasn't changed since the in-memory version (Assignment 1); only the storage layer changed from a Python list to a SQL database.

## Why SQLite

SQLite was chosen because it requires **no separate server or installation** — it's a single file (`tasks.db`) that Python's built-in `sqlite3` module can read and write directly. This makes it ideal for learning how an API talks to a real database, before moving on to something like PostgreSQL that needs its own server process.

## Where the database is stored

The database lives in a single file named `tasks.db`, created automatically in the project's root folder the first time the app runs. If the file or the `tasks` table doesn't exist yet, the app creates them on startup, and seeds 3 example tasks only if the table is empty.

## How to run it

**Requirements:** Python 3.10+

```bash
# 1. Clone the repo
git clone https://github.com/Fatimaaa18/todo-crud-api-python.git
cd todo-crud-api-python

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install fastapi uvicorn

# 4. Run the server
uvicorn main:app --reload
```

The server starts at `http://localhost:8000`, and `tasks.db` is created automatically on first run.
Interactive API docs (Swagger UI): `http://localhost:8000/docs`

## Endpoints

| Method | Endpoint         | Description                              |
|--------|------------------|---------------------------------------------|
| GET    | `/`              | Returns basic API info                       |
| GET    | `/health`        | Health check — returns `{"status": "ok"}`    |
| GET    | `/tasks`         | Returns all tasks from the database          |
| GET    | `/tasks/{id}`    | Returns a single task by ID                  |
| POST   | `/tasks`         | Inserts a new task into the database         |
| PUT    | `/tasks/{id}`    | Updates an existing task's title/done        |
| DELETE | `/tasks/{id}`    | Deletes a task from the database             |

## Example request

```bash
curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d "{\"title\":\"Buy milk\"}"
```

Response:

```
HTTP/1.1 201 Created
content-type: application/json

{"id": 4, "title": "Buy milk", "done": false}
```

## Exploring the database manually

Using [DB Browser for SQLite](https://sqlitebrowser.org/), I opened `tasks.db` and ran a few queries directly against the table to confirm the API and the database stay in sync:

```sql
SELECT * FROM tasks WHERE done = 1;
```

Changes made this way (e.g. marking tasks as done, deleting completed tasks) are immediately reflected the next time `GET /tasks` is called — confirming the API always reads live from the database, not from any cached copy.

![DB Browser screenshot](db-browser-screenshot.png)

## Status codes used

| Code | Meaning                          |
|------|-------------------------------------|
| 200  | Successful GET / PUT                |
| 201  | Task created successfully           |
| 204  | Task deleted successfully           |
| 400  | Invalid input (e.g. empty title)    |
| 404  | Task not found                      |

