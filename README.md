# To-Do CRUD API (Python / FastAPI)

A simple in-memory To-Do list API built with **FastAPI**, supporting full CRUD (Create, Read, Update, Delete) operations. Built as part of the FlyRank Backend AI Engineering internship (Week 2 assignment).

## What this is

This API lets you manage a list of tasks — create new tasks, view them, update their title/status, and delete them. Data is stored in memory (no database yet), so it resets every time the server restarts.

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

The server will start at `http://localhost:8000`.
Interactive API docs (Swagger UI) are available at `http://localhost:8000/docs`.

## Endpoints

| Method | Endpoint         | Description                              |
|--------|------------------|-------------------------------------------|
| GET    | `/`              | Returns basic API info                    |
| GET    | `/health`        | Health check — returns `{"status": "ok"}` |
| GET    | `/tasks`         | Returns the full list of tasks            |
| GET    | `/tasks/{id}`    | Returns a single task by ID                |
| POST   | `/tasks`         | Creates a new task                         |
| PUT    | `/tasks/{id}`    | Updates an existing task's title/done      |
| DELETE | `/tasks/{id}`    | Deletes a task                             |

## Example request

```bash
curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d "{\"title\":\"Buy milk\"}"
```

Response:

```
HTTP/1.1 201 Created
content-type: application/json

{"id": 4, "title": "Buy milk", "done": false}


## Status codes used

| Code | Meaning                          |
|------|-----------------------------------|
| 200  | Successful GET / PUT               |
| 201  | Task created successfully          |
| 204  | Task deleted successfully          |
| 400  | Invalid input (e.g. empty title)   |
| 404  | Task not found                     |