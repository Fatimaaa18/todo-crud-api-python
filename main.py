from fastapi import FastAPI , HTTPException
from pydantic import BaseModel
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

tasks = [{"id" : 1 , "title" : "Internship work" , "done" : True} , {"id" : 2 , "title" : "Course Work" , "done" : False} , {"id" : 3 , "title" : "Uni work" , "done" : False}]

@app.get("/tasks")
def all_tasks():
    return tasks

@app.get("/tasks/{task_id}")
def spec_task(task_id : int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

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
