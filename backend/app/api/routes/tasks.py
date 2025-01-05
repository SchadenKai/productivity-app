from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app import crud
from app.models import ProjectCreate, ProjectRead, TaskCreate, TaskRead
from app.api.deps import get_db

router = APIRouter()

@router.post("/tasks/", response_model=TaskRead)
def create_task(*, session: Session = Depends(get_db), task_in: TaskCreate):
    return crud.create_task(session=session, task_in=task_in)

@router.get("/tasks/{task_id}", response_model=TaskRead)
def read_task(*, session: Session = Depends(get_db), task_id: uuid.UUID):
    task = crud.get_task(session=session, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task