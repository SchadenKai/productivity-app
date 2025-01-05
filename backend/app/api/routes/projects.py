from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app import crud
from app.models import ProjectCreate, ProjectRead, TaskCreate, TaskRead
from app.api.deps import get_db

router = APIRouter()

@router.post("/projects/", response_model=ProjectRead)
def create_project(*, session: Session = Depends(get_db), project_in: ProjectCreate):
    return crud.create_project(session=session, project_in=project_in)

@router.get("/projects/{project_id}", response_model=ProjectRead)
def read_project(*, session: Session = Depends(get_db), project_id: uuid.UUID):
    project = crud.get_project(session=session, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project