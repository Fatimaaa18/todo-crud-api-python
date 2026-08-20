from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_connection():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title TEXT,
            done BOOLEAN
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

def seed_data():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()["count"]

    if count == 0:
        cursor.execute("INSERT INTO tasks (title, done) VALUES (%s, %s)", ("Internship work", True))
        cursor.execute("INSERT INTO tasks (title, done) VALUES (%s, %s)", ("Course Work", False))
        cursor.execute("INSERT INTO tasks (title, done) VALUES (%s, %s)", ("Uni work", False))

    conn.commit()
    cursor.close()
    conn.close()

create_table()
seed_data()

app = FastAPI()

class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: str
    done: bool

class AuthRequest(BaseModel):
    email: str
    password: str

@app.post("/auth/signup" , status_code = 201)
def signup(auth: AuthRequest):
    if not auth.email or not auth.password:
        raise HTTPException(status_code=400 , detail="Email and password both are required!")

    try:
        result = supabase.auth.sign_up({"email": auth.email, "password": auth.password})
        return result.user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login")
def login(auth: AuthRequest):
    if not auth.email or not auth.password:
        raise HTTPException(status_code=400, detail="Email and password are required")

     
    try:
        result = supabase.auth.sign_in_with_password({"email": auth.email, "password": auth.password})
        return {
            "access_token": result.session.access_token,
            "refresh_token": result.session.refresh_token
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid login credentials")

@app.get("/public/info")
def public_info():
    return {"message": "Welcome stranger! This info is public."}


@app.get("/protected/profile")
def protected_profile(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Access token required")

    token = authorization.split(" ")[1]

    try:
        user_response = supabase.auth.get_user(token)
        user = user_response.user
        return {
            "id": user.id,
            "email": user.email,
            "created_at": user.created_at
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@app.get("/")
def read_root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
def read_route():
    return {"status": "ok"}

@app.get("/tasks")
def all_tasks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    return row

@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    if not task.title or task.title.strip() == "":
        raise HTTPException(status_code=400, detail="Title is required")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id",
        (task.title, False)
    )
    new_id = cursor.fetchone()["id"]
    conn.commit()
    cursor.close()
    conn.close()

    return {"id": new_id, "title": task.title, "done": False}

@app.put("/tasks/{task_id}")
def update_task(task_id: int, updated: TaskUpdate):
    if not updated.title or updated.title.strip() == "":
        raise HTTPException(status_code=400, detail="Title is required")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    row = cursor.fetchone()

    if row is None:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    cursor.execute(
        "UPDATE tasks SET title = %s, done = %s WHERE id = %s",
        (updated.title, updated.done, task_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return {"id": task_id, "title": updated.title, "done": updated.done}

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    row = cursor.fetchone()

    if row is None:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return