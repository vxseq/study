def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"message": "Backend работает"}


def test_site_opens(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Обзор проектов" in response.text


def test_create_and_get_projects(client):
    created = client.post(
        "/api/projects/", json={"name": "Проект 1", "description": "Описание"}
    )
    assert created.status_code == 201
    project = created.json()
    assert project["status"] == "В сроке"

    projects = client.get("/api/projects/")
    assert projects.status_code == 200
    assert len(projects.json()) == 1
    assert projects.json()[0]["name"] == "Проект 1"
    assert client.get(f"/api/projects/{project['id']}").status_code == 200


def test_edit_and_delete_project(client):
    project_id = client.post("/api/projects/", json={"name": "Было"}).json()["id"]
    changed = client.put(f"/api/projects/{project_id}", json={"name": "Стало"})
    assert changed.status_code == 200
    assert changed.json()["name"] == "Стало"
    assert client.delete(f"/api/projects/{project_id}").status_code == 200
    assert client.get(f"/api/projects/{project_id}").status_code == 404


def test_invalid_project(client):
    assert client.get("/api/projects/999/status").status_code == 404
    assert client.put("/api/projects/999", json={"name": "X"}).status_code == 404
    assert client.post("/api/projects/", json={"name": ""}).status_code == 422
