# To-Do CRUD API (Python / FastAPI)

A To-Do list API built with **FastAPI**, evolving across three stages: from an in-memory list, to SQLite, to a fully containerized **PostgreSQL + Docker** stack. Built as part of the FlyRank Backend AI Engineering internship.

The API itself — the endpoints, request/response shapes, and status codes — never changed across all three stages. Only the storage layer underneath it changed. That's the core lesson this project demonstrates: **the API layer and the data layer are separate concerns.**

---

## Project evolution

| Stage | Assignment | Storage | What changed |
|-------|-----------|---------|----------------|
| 1 | BE-01 — Build your first CRUD API | In-memory Python list | Data lived in RAM only; lost on restart |
| 2 | BE-02 — Connect to the database | SQLite (`tasks.db`) | Data persisted in a local file; survived app restarts |
| 3 | BE-03 — Containerize your stack | PostgreSQL in Docker | Data persisted in a Docker volume; survived both app **and** container restarts; whole stack runs with one command |

---

## Stage 1: In-memory CRUD API

Built the four CRUD operations (Create, Read, Update, Delete) as FastAPI endpoints, backed by a plain Python list. This established the API contract — the URLs, request bodies, and status codes — that every later stage had to preserve exactly.

- `GET /tasks`, `GET /tasks/{id}`, `POST /tasks`, `PUT /tasks/{id}`, `DELETE /tasks/{id}`
- Input validation: empty `title` → `400`
- Unknown `id` → `404`
- Swagger UI auto-generated at `/docs`

## Stage 2: SQLite persistence

Replaced the in-memory list with a real SQLite database (`tasks.db`), using Python's built-in `sqlite3` module. The database and table are created automatically on first run, and three example tasks are seeded only if the table is empty — so restarting the app no longer wipes the data.

- All five endpoints rewritten to run SQL queries (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) instead of manipulating a list
- Verified manually with **DB Browser for SQLite** — ran queries like `SELECT * FROM tasks WHERE done = 1;` directly against the database and confirmed the API reflected the changes immediately

## Stage 3: PostgreSQL + Docker (current stage)

Swapped SQLite for a production-style **PostgreSQL** database, running in **Docker**, with the entire stack (app + database) starting from a single command.

**What changed under the hood:**
- `sqlite3` → `psycopg2-binary` (PostgreSQL driver for Python)
- Connection string now comes from a `.env` file (gitignored) instead of a hardcoded file path
- `INTEGER PRIMARY KEY` → `SERIAL PRIMARY KEY`; `?` placeholders → `%s` placeholders — the only real syntax differences between SQLite and Postgres
- **The routes and service logic did not change** — same endpoints, same validation, same status codes. Only the functions that talk to the database were rewritten.

**Persistence was proven by:**
1. Creating a new task via `POST /tasks` through Swagger UI while the stack was running
2. Stopping the entire stack (`Ctrl+C` on `docker compose up`)
3. Restarting it (`docker compose up`)
4. Calling `GET /tasks` again and confirming the new task was still there — proving the data lives in the Docker volume, not in the container's temporary filesystem

---

## How to run it

**Requirements:** Docker Desktop installed and running.

```bash
# 1. Clone the repo
git clone https://github.com/Fatimaaa18/todo-crud-api-python.git
cd todo-crud-api-python

# 2. Create a .env file based on the example
cp .env.example .env
# then edit .env if you want a different password

# 3. Start the whole stack (app + Postgres) with one command
docker compose up
```

The app will be available at `http://localhost:8000`, and Swagger UI at `http://localhost:8000/docs`.
On first run, Postgres creates the `tasks` table and seeds 3 example tasks automatically.

**To run the app without Docker (local dev only):**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn main:app --reload
```
(Note: a Postgres instance must be reachable at the `DATABASE_URL` in `.env` for this to work.)

---

## Endpoints

| Method | Endpoint         | Description                              |
|--------|------------------|---------------------------------------------|
| GET    | `/`              | Returns basic API info                       |
| GET    | `/health`        | Health check — returns `{"status": "ok"}`    |
| GET    | `/tasks`         | Returns all tasks                            |
| GET    | `/tasks/{id}`    | Returns a single task by ID                  |
| POST   | `/tasks`         | Creates a new task                           |
| PUT    | `/tasks/{id}`    | Updates an existing task's title/done        |
| DELETE | `/tasks/{id}`    | Deletes a task                               |

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

## Status codes used

| Code | Meaning                          |
|------|-------------------------------------|
| 200  | Successful GET / PUT                |
| 201  | Task created successfully           |
| 204  | Task deleted successfully           |
| 400  | Invalid input (e.g. empty title)    |
| 404  | Task not found                      |

## Project structure

```
to-do-crud-api-python/
├── main.py                 # FastAPI app, routes, and database logic
├── requirements.txt        # Python dependencies
├── Dockerfile               # Builds the app's container image
├── docker-compose.yml       # Runs app + Postgres together
├── .env.example              # Template for required environment variables
├── .gitignore
└── README.md
```

## What this project demonstrates

Across all three assignments, the API's URLs, request bodies, and responses never changed. Only the storage layer did — first an in-memory list, then SQLite, then Postgres in Docker. This separation between the **API layer** (what the application does) and the **data layer** (where it stores its data) is one of the foundational ideas in backend engineering, and it's what makes moving between databases in a real project possible without rewriting the whole app.