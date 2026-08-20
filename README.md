# To-Do CRUD API (Python / FastAPI)

A To-Do list API built with **FastAPI**, evolving across four stages: from an in-memory list, to SQLite, to a fully containerized **PostgreSQL + Docker** stack, and finally to a secure **authenticated API with Supabase login, JWT tokens, and protected routes**.

The API itself — the endpoints, request/response shapes, and status codes — never changed across all three stages. Only the storage layer underneath it changed. That's the core lesson this project demonstrates: **the API layer and the data layer are separate concerns.**

---

## Project evolution

| Stage | Assignment                        | Storage               | What changed                                                                                                       |
| ----- | --------------------------------- | --------------------- | ------------------------------------------------------------------------------------------------------------------ |
| 1     | BE-01 — Build your first CRUD API | In-memory Python list | Data lived in RAM only; lost on restart                                                                            |
| 2     | BE-02 — Connect to the database   | SQLite (`tasks.db`)   | Data persisted in a local file; survived app restarts                                                              |
| 3     | BE-03 — Containerize your stack   | PostgreSQL in Docker  | Data persisted in a Docker volume; survived both app **and** container restarts; whole stack runs with one command |
| 4     | BE-04 — Auth — Login & Protect    | Supabase Auth + JWT   | Added user signup, login, logout, token verification, and protected routes                                         |

---

## Stage 1: In-memory CRUD API

Built the four CRUD operations (Create, Read, Update, Delete) as FastAPI endpoints, backed by a plain Python list. This established the API contract — the URLs, request bodies, and status codes — that every later stage had to preserve exactly.

* `GET /tasks`, `GET /tasks/{id}`, `POST /tasks`, `PUT /tasks/{id}`, `DELETE /tasks/{id}`

* Input validation: empty `title` → `400`

* Unknown `id` → `404`

* Swagger UI auto-generated at `/docs`

## Stage 2: SQLite persistence

Replaced the in-memory list with a real SQLite database (`tasks.db`), using Python's built-in `sqlite3` module. The database and table are created automatically on first run, and three example tasks are seeded only if the table is empty — so restarting the app no longer wipes the data.

* All five endpoints rewritten to run SQL queries (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) instead of manipulating a list

* Verified manually with **DB Browser for SQLite** — ran queries like `SELECT * FROM tasks WHERE done = 1;` directly against the database and confirmed the API reflected the changes immediately

## Stage 3: PostgreSQL + Docker (current stage)

Swapped SQLite for a production-style **PostgreSQL** database, running in **Docker**, with the entire stack (app + database) starting from a single command.

**What changed under the hood:**

* `sqlite3` → `psycopg2-binary` (PostgreSQL driver for Python)

* Connection string now comes from a `.env` file (gitignored) instead of a hardcoded file path

* `INTEGER PRIMARY KEY` → `SERIAL PRIMARY KEY`; `?` placeholders → `%s` placeholders — the only real syntax differences between SQLite and Postgres

* **The routes and service logic did not change** — same endpoints, same validation, same status codes. Only the functions that talk to the database were rewritten.

**Persistence was proven by:**

1. Creating a new task via `POST /tasks` through Swagger UI while the stack was running

2. Stopping the entire stack (`Ctrl+C` on `docker compose up`)

3. Restarting it (`docker compose up`)

4. Calling `GET /tasks` again and confirming the new task was still there — proving the data lives in the Docker volume, not in the container's temporary filesystem

---

## Stage 4: Authentication — Login & Protect

Added authentication to the backend using **Supabase Auth**, allowing users to sign up, log in, receive secure **JWT access tokens**, and access protected API routes.

**What changed:**

* Added `POST /auth/signup` for creating user accounts
* Added `POST /auth/login` for authenticating users and returning access/refresh tokens
* Added `POST /auth/logout` as a protected logout endpoint
* Added `GET /public/info` as a public endpoint
* Added `GET /protected/profile` as a protected endpoint
* Added Bearer token authentication using the `Authorization` header
* Added token verification through Supabase
* Extracted authentication checking into reusable middleware/dependency
* Added Swagger UI support for Bearer authentication
* Added environment variables for Supabase configuration
* Added proper `400` and `401` responses for invalid input and authentication failures

**Authentication flow:**

```text
Client
   ↓
Supabase Auth
   ↓
JWT Access Token
   ↓
FastAPI Backend
   ↓
Token Verification
   ↓
Protected Route
```

Protected endpoints require:

```text
Authorization: Bearer <access_token>
```

**Authentication endpoints:**

| Method | Endpoint             | Description                            | Auth Required |
| ------ | -------------------- | -------------------------------------- | ------------- |
| POST   | `/auth/signup`       | Creates a new user account             | No            |
| POST   | `/auth/login`        | Authenticates user and returns tokens  | No            |
| POST   | `/auth/logout`       | Logs out the authenticated user        | Yes           |
| GET    | `/public/info`       | Returns public information             | No            |
| GET    | `/protected/profile` | Returns authenticated user information | Yes           |

**Authentication status codes:**

| Code  | Meaning                                  |
| ----- | ---------------------------------------- |
| `200` | Successful login / authenticated request |
| `201` | User account created                     |
| `204` | Successful logout                        |
| `400` | Missing or invalid input                 |
| `401` | Missing, invalid, or expired token       |

Supabase credentials are stored in environment variables and should never be committed to GitHub.

---

**## How to run it**

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

For the authentication features, add your Supabase configuration to `.env`:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
```

**To run the app without Docker (local dev only):**

```bash
python -m venv venv
venv\Scripts\activate       # Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

(Note: a Postgres instance must be reachable at the `DATABASE_URL` in `.env` for this to work.)

**---**

**## Endpoints**

| Method | Endpoint             | Description                               |
| ------ | -------------------- | ----------------------------------------- |
| GET    | `/`                  | Returns basic API info                    |
| GET    | `/health`            | Health check — returns `{"status": "ok"}` |
| GET    | `/tasks`             | Returns all tasks                         |
| GET    | `/tasks/{id}`        | Returns a single task by ID               |
| POST   | `/tasks`             | Creates a new task                        |
| PUT    | `/tasks/{id}`        | Updates an existing task's title/done     |
| DELETE | `/tasks/{id}`        | Deletes a task                            |
| POST   | `/auth/signup`       | Creates a new user account                |
| POST   | `/auth/login`        | Authenticates user and returns JWT tokens |
| POST   | `/auth/logout`       | Logs out the authenticated user           |
| GET    | `/public/info`       | Returns public information                |
| GET    | `/protected/profile` | Returns protected user profile data       |

**## Example request**

```bash
curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d "{\"title\":\"Buy milk\"}"
```

Response:

```text
HTTP/1.1 201 Created

content-type: application/json

{"id": 4, "title": "Buy milk", "done": false}
```

**## Status codes used**

| Code | Meaning                                                 |
| ---- | ------------------------------------------------------- |
| 200  | Successful GET / PUT / login                            |
| 201  | Task/user created successfully                          |
| 204  | Task deleted / logout successful                        |
| 400  | Invalid input (e.g. empty title or missing auth fields) |
| 401  | Missing, invalid, or expired authentication token       |
| 404  | Task not found                                          |

**## Project structure**

```text
to-do-crud-api-python/

├── main.py                 # FastAPI app, routes, and database logic
├── requirements.txt        # Python dependencies
├── Dockerfile              # Builds the app's container image
├── docker-compose.yml      # Runs app + Postgres together
├── .env.example            # Template for required environment variables
├── .gitignore
└── README.md
```

**## What this project demonstrates**

Across all four assignments, the project evolved from an in-memory CRUD API to SQLite, then PostgreSQL in Docker, and finally an authenticated API with protected routes.

The storage layer evolved through:

**in-memory list → SQLite → PostgreSQL**

while authentication was added as a separate security layer using **Supabase Auth and JWTs**.

This project demonstrates the separation between the **API layer**, **data layer**, and **authentication layer** — allowing storage and security concerns to evolve without rewriting the core CRUD functionality.

It also demonstrates:

* FastAPI REST API development
* CRUD operations
* SQLite and SQL
* PostgreSQL
* Docker and Docker Compose
* Persistent database storage
* Repository-based database access
* Supabase authentication
* JWT access tokens
* Bearer token authentication
* Protected API routes
* Authentication middleware/dependencies
* Swagger/OpenAPI
* Environment variables
* Git and GitHub

**---**

## Internship Context

This project was built as part of my **Backend AI Engineering Internship at FlyRank AI**.

The four assignments were completed in the following order:

1. **BE-01 — Build your first CRUD API**
2. **BE-02 — Connecting your CRUD to the database**
3. **BE-03 — Containerize your stack**
4. **BE-04 — Auth — Login & Protect**

Each assignment extended the backend from the previous stage, providing hands-on experience with API development, database persistence, containerization, and authentication.
