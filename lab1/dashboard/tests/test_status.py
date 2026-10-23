from datetime import datetime, timedelta


def project(client, name="Проект"):
    response = client.post("/api/projects/", json={"name": name})
    assert response.status_code == 201
    return response.json()["id"]


def user(client):
    response = client.post("/api/users/", json={"name": "Иван", "role": "Аналитик"})
    assert response.status_code == 201
    return response.json()["id"]


def task(client, project_id, status="В работе", deadline=None, user_id=None):
    response = client.post(
        "/api/tasks/",
        json={
            "title": "Тестовая задача",
            "status": status,
            "deadline": deadline,
            "project_id": project_id,
            "user_id": user_id,
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def get_status(client, project_id):
    response = client.get(f"/api/projects/{project_id}/status")
    assert response.status_code == 200
    return response.json()["status"]


def test_green_status(client):
    project_id = project(client)
    task(client, project_id, deadline=(datetime.now() + timedelta(days=2)).isoformat())
    assert get_status(client, project_id) == "В сроке"


def test_yellow_status(client):
    project_id = project(client)
    task(client, project_id, deadline=(datetime.now() - timedelta(days=2)).isoformat())
    assert get_status(client, project_id) == "Есть риски"
    # Статус должен измениться и в общем списке проектов.
    assert client.get("/api/projects/").json()[0]["status"] == "Есть риски"


def test_red_status_has_priority(client):
    project_id = project(client)
    task(client, project_id, deadline=(datetime.now() - timedelta(days=2)).isoformat())
    task(client, project_id, status="Блокер")
    assert get_status(client, project_id) == "Блокер"


def test_done_overdue_task_is_green(client):
    project_id = project(client)
    task(
        client,
        project_id,
        status="Готово",
        deadline=(datetime.now() - timedelta(days=4)).isoformat(),
    )
    assert get_status(client, project_id) == "В сроке"


def test_status_changes_after_edit(client):
    project_id = project(client)
    task_id = task(client, project_id, status="Блокер")
    assert get_status(client, project_id) == "Блокер"
    updated = client.put(
        f"/api/tasks/{task_id}",
        json={"title": "Исправили", "project_id": project_id, "status": "Готово"},
    )
    assert updated.status_code == 200
    assert get_status(client, project_id) == "В сроке"


def test_status_changes_after_delete(client):
    project_id = project(client)
    task_id = task(client, project_id, status="Блокер")
    assert client.delete(f"/api/tasks/{task_id}").status_code == 200
    assert get_status(client, project_id) == "В сроке"


def test_move_task_between_projects(client):
    old_id = project(client, "Первый")
    new_id = project(client, "Второй")
    task_id = task(client, old_id, status="Блокер")
    assert get_status(client, old_id) == "Блокер"
    response = client.put(
        f"/api/tasks/{task_id}",
        json={"title": "Переехала", "project_id": new_id, "status": "Блокер"},
    )
    assert response.status_code == 200
    assert get_status(client, old_id) == "В сроке"
    assert get_status(client, new_id) == "Блокер"


def test_create_task_with_user(client):
    project_id = project(client)
    user_id = user(client)
    task_id = task(client, project_id, user_id=user_id)
    response = client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["user_id"] == user_id
    assert len(client.get(f"/api/tasks/?project_id={project_id}").json()) == 1


def test_task_invalid_links(client):
    project_id = project(client)
    response = client.post("/api/tasks/", json={"title": "Тест", "project_id": 999})
    assert response.status_code == 404
    response = client.post(
        "/api/tasks/", json={"title": "Тест", "project_id": project_id, "user_id": 999}
    )
    assert response.status_code == 404
    response = client.post(
        "/api/tasks/", json={"title": "Тест", "project_id": project_id, "status": "Ошибка"}
    )
    assert response.status_code == 422


def test_delete_project_removes_tasks(client):
    project_id = project(client)
    task(client, project_id)
    assert client.delete(f"/api/projects/{project_id}").status_code == 200
    assert client.get("/api/tasks/").json() == []


def test_time_sensitive_status_rechecked_when_opening_dashboard(client):
    project_id = project(client)
    # Установили просроченный дедлайн, а затем проверили список.
    task(client, project_id, deadline=(datetime.now() - timedelta(hours=1)).isoformat())
    response = client.get("/api/projects/")
    assert response.json()[0]["status"] == "Есть риски"


def test_deadline_with_timezone(client):
    project_id = project(client)
    # API принимает даты с суффиксом Z (UTC) без ошибки сравнения.
    response = client.post(
        "/api/tasks/",
        json={"title": "Время UTC", "project_id": project_id, "deadline": "2020-01-01T12:00:00Z"},
    )
    assert response.status_code == 201
    assert get_status(client, project_id) == "Есть риски"
