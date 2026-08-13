from fastapi import FastAPI , HTTPException
from pydantic import BaseModel
import sqlite3

def get_connection():
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT,
            done BOOLEAN
        )
    """)
    conn.commit()
    conn.close()

def seed_data():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]
    
    if count == 0:
        cursor.execute("INSERT INTO tasks (id, title, done) VALUES (1, 'Internship work', 1)")
        cursor.execute("INSERT INTO tasks (id, title, done) VALUES (2, 'Course Work', 0)")
        cursor.execute("INSERT INTO tasks (id, title, done) VALUES (3, 'Uni work', 0)")
        
    conn.commit()
    conn.close()

create_table()
seed_data()

app = FastAPI()
class TaskCreate(BaseModel):
    title: str
class TaskUpdate(BaseModel):
    title: str
    done: bool

@app.get("/")
def read_root():
    return{ "name": "Task API", "version": "1.0", "endpoints": ["/tasks"] }

@app.get("/health")
def read_route():
    return{"status" : "ok"}


@app.get("/tasks")
def all_tasks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    return dict(row)

@app.post("/tasks" , status_code = 201)
def cr_task(task: TaskCreate):
    if not task.title or task.title.strip() == "":
        raise HTTPException(status_code=400, detail="Title is required")
    new_id = max(t["id"] for t in tasks) + 1 if tasks else 1
    new_task = {"id" : new_id , "title" : task.title , "done" : False}
    tasks.append(new_task)
    return new_task

@app.put("/tasks/{task_id}")
def upd_task(task_id: int , updated: TaskUpdate):
    if not updated.title or updated.title.strip() == "":
       raise HTTPException(status_code=400, detail="Title is required")
    for task in tasks:
        if task["id"] == task_id:
           task["title"] = updated.title
           task["done"] = updated.done
           return task

    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@app.delete("/tasks/{task_id}")
def task_del(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)
            return
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
