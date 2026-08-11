from fastapi import FastAPI , HTTPException
app = FastAPI()

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


