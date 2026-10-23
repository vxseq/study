from datetime import datetime

from sqlalchemy.orm import Session

from models import Project, Task


def calculate_project_status(project: Project, db: Session) -> str:
    """Блокер важнее просрочки; выполненные задачи не считаются просроченными."""
    tasks = db.query(Task).filter(Task.project_id == project.id).all()

    if any(task.status == "Блокер" for task in tasks):
        return "Блокер"

    now = datetime.now()
    if any(
        task.deadline is not None
        and task.deadline < now
        and task.status != "Готово"
        for task in tasks
    ):
        return "Есть риски"

    return "В сроке"


def update_project_status(project: Project, db: Session) -> None:
    project.status = calculate_project_status(project, db)


def refresh_all_project_statuses(db: Session) -> None:
    """При открытии дашборда проверяем сроки, даже если никто не изменял задачи."""
    for project in db.query(Project).all():
        update_project_status(project, db)
    db.commit()
