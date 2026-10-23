"""Необязательные демонстрационные данные: python seed.py."""

from datetime import datetime, timedelta

from database import Base, SessionLocal, engine
from models import Project, Task, User
from services import update_project_status


Base.metadata.create_all(bind=engine)


def main():
    with SessionLocal() as db:
        if db.query(Project).first():
            print("Проекты уже есть. Демонстрационные данные не добавлены.")
            return

        analyst = User(name="Анна Смирнова", role="Аналитик")
        developer = User(name="Иван Петров", role="Разработчик")
        manager = User(name="Мария Кузнецова", role="Руководитель проекта")
        db.add_all([analyst, developer, manager])
        db.flush()

        p1 = Project(name="Внедрение CRM", description="Настройка CRM и обучение сотрудников")
        p2 = Project(name="Обновление серверов", description="Перенос сервисов на новые серверы")
        p3 = Project(name="Интеграция с API", description="Связь внутренней системы с внешним API")
        db.add_all([p1, p2, p3])
        db.flush()

        db.add_all(
            [
                Task(title="Настроить карточки клиентов", status="В работе", project_id=p1.id, user_id=developer.id, deadline=datetime.now() + timedelta(days=4)),
                Task(title="Согласовать требования", status="Готово", project_id=p1.id, user_id=analyst.id, deadline=datetime.now() - timedelta(days=2)),
                Task(title="Перенести тестовый сервер", status="В работе", project_id=p2.id, user_id=developer.id, deadline=datetime.now() - timedelta(days=1)),
                Task(title="Исправить ошибку авторизации", status="Блокер", project_id=p3.id, user_id=developer.id, deadline=datetime.now() + timedelta(days=3)),
                Task(title="Подготовить документацию", status="В работе", project_id=p3.id, user_id=analyst.id, deadline=datetime.now() + timedelta(days=7)),
            ]
        )
        db.flush()
        for project in [p1, p2, p3]:
            update_project_status(project, db)
        db.commit()
        print("Готово: 3 проекта, 3 участника, 5 задач.")


if __name__ == "__main__":
    main()
