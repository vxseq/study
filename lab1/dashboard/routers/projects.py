from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Project, Task
from schemas import ProjectCreate, ProjectResponse
from services import refresh_all_project_statuses, update_project_status


router = APIRouter(prefix="/api/projects", tags=["Projects"])


def find_project(project_id: int, db: Session) -> Project:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Проект не найден")
    return project


@router.post("/", response_model=ProjectResponse, status_code=201)
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(**data.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/", response_model=list[ProjectResponse])
def get_projects(db: Session = Depends(get_db)):
    refresh_all_project_statuses(db)
    return db.query(Project).order_by(Project.id.desc()).all()


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = find_project(project_id, db)
    update_project_status(project, db)
    db.commit()
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def edit_project(project_id: int, data: ProjectCreate, db: Session = Depends(get_db)):
    project = find_project(project_id, db)
    project.name = data.name
    project.description = data.description
    update_project_status(project, db)
    db.commit()
    return project


@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = find_project(project_id, db)
    # Сначала удаляем задачи проекта, затем сам проект.
    db.query(Task).filter(Task.project_id == project_id).delete()
    db.delete(project)
    db.commit()
    return {"message": "Проект удалён"}


@router.get("/{project_id}/status")
def get_project_status(project_id: int, db: Session = Depends(get_db)):
    project = find_project(project_id, db)
    update_project_status(project, db)
    db.commit()
    return {"project_id": project.id, "status": project.status}
