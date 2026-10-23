from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Project, Task, User
from schemas import TaskCreate, TaskResponse
from services import update_project_status


router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


def check_links(data: TaskCreate, db: Session) -> Project:
    project = db.get(Project, data.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Проект не найден")
    if data.user_id is not None and db.get(User, data.user_id) is None:
        raise HTTPException(status_code=404, detail="Исполнитель не найден")
    return project


def find_task(task_id: int, db: Session) -> Task:
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task


@router.post("/", response_model=TaskResponse, status_code=201)
def create_task(data: TaskCreate, db: Session = Depends(get_db)):
    project = check_links(data, db)
    task = Task(**data.model_dump())
    db.add(task)
    db.flush()  # Записываем задачу перед пересчётом статуса.
    update_project_status(project, db)
    db.commit()
    db.refresh(task)
    return task


@router.get("/", response_model=list[TaskResponse])
def get_tasks(project_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Task)
    if project_id is not None:
        query = query.filter(Task.project_id == project_id)
    return query.order_by(Task.id.desc()).all()


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    return find_task(task_id, db)


@router.put("/{task_id}", response_model=TaskResponse)
def edit_task(task_id: int, data: TaskCreate, db: Session = Depends(get_db)):
    task = find_task(task_id, db)
    new_project = check_links(data, db)
    old_project_id = task.project_id

    for field, value in data.model_dump().items():
        setattr(task, field, value)

    db.flush()
    update_project_status(new_project, db)
    if old_project_id != new_project.id:
        update_project_status(db.get(Project, old_project_id), db)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = find_task(task_id, db)
    project = db.get(Project, task.project_id)
    db.delete(task)
    db.flush()
    update_project_status(project, db)
    db.commit()
    return {"message": "Задача удалена"}
