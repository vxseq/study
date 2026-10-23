// Простой frontend на обычном JavaScript, без дополнительных библиотек.
const state = { projects: [], tasks: [], users: [] };
const $ = (selector) => document.querySelector(selector);
let toastTimeout;

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[char]);
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  if (!response.ok) {
    const result = await response.json().catch(() => ({}));
    const detail = result.detail;
    const message = typeof detail === "string" ? detail : "Проверьте введённые данные";
    throw new Error(message);
  }
  return response.json();
}

function toast(message, isError = false) {
  const element = $("#toast");
  element.textContent = message;
  element.classList.toggle("error", isError);
  element.classList.add("visible");
  clearTimeout(toastTimeout);
  toastTimeout = setTimeout(() => element.classList.remove("visible"), 3200);
}

function statusClass(status) {
  return ({ "В сроке": "good", "Есть риски": "risk", "Блокер": "block", "Готово": "done", "В работе": "progress" })[status] || "progress";
}

function badge(status) {
  return `<span class="status ${statusClass(status)}">${escapeHtml(status)}</span>`;
}

function formatDate(value) {
  if (!value) return "Не указан";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "Не указан" : date.toLocaleDateString("ru-RU", { day: "2-digit", month: "short", year: "numeric" });
}

function isOverdue(task) {
  return task.deadline && task.status !== "Готово" && new Date(task.deadline) < new Date();
}

async function loadData() {
  const [projects, tasks, users] = await Promise.all([
    api("/api/projects/"), api("/api/tasks/"), api("/api/users/"),
  ]);
  state.projects = projects;
  state.tasks = tasks;
  state.users = users;
  render();
}

function render() {
  $("#count-all").textContent = state.projects.length;
  $("#count-good").textContent = state.projects.filter((p) => p.status === "В сроке").length;
  $("#count-risk").textContent = state.projects.filter((p) => p.status === "Есть риски").length;
  $("#count-blocked").textContent = state.projects.filter((p) => p.status === "Блокер").length;
  $("#project-total").textContent = state.projects.length;
  renderProjects();
  renderProjectFilter();
  renderTasks();
}

function renderProjects() {
  const search = $("#search-projects").value.trim().toLowerCase();
  const filter = $("#filter-status").value;
  const projects = state.projects.filter((p) =>
    p.name.toLowerCase().includes(search) && (filter === "all" || p.status === filter)
  );
  if (!projects.length) {
    $("#project-grid").innerHTML = `<div class="empty"><span class="empty-symbol">▦</span><b>Проекты не найдены</b><p>Создайте новый проект или измените фильтр.</p><button type="button" class="btn btn-primary" data-action="new-project">＋ Новый проект</button></div>`;
    return;
  }
  $("#project-grid").innerHTML = projects.map((p) => {
    const tasks = state.tasks.filter((t) => t.project_id === p.id);
    return `<article class="project-card">
      ${badge(p.status)}
      <div class="card-actions"><button class="icon-btn" data-action="edit-project" data-id="${p.id}" aria-label="Редактировать проект" title="Редактировать">✎</button><button class="icon-btn" data-action="delete-project" data-id="${p.id}" aria-label="Удалить проект" title="Удалить">✕</button></div>
      <h3 class="project-card-title">${escapeHtml(p.name)}</h3><p class="project-desc">${escapeHtml(p.description || "Описание не добавлено")}</p>
      <div class="project-card-bottom"><small>☷ ${tasks.length} задач · ${tasks.filter((t) => t.status === "Готово").length} выполнено</small><button class="mini-link" data-action="view-tasks" data-id="${p.id}">Задачи →</button></div>
    </article>`;
  }).join("");
}

function renderProjectFilter() {
  const select = $("#task-project-filter");
  const current = select.value;
  select.innerHTML = '<option value="all">Все проекты</option>' + state.projects.map((p) =>
    `<option value="${p.id}">${escapeHtml(p.name)}</option>`
  ).join("");
  select.value = [...select.options].some((o) => o.value === current) ? current : "all";
}

function renderTasks() {
  const current = $("#task-project-filter").value;
  const tasks = state.tasks.filter((t) => current === "all" || t.project_id === Number(current));
  $("#task-total").textContent = tasks.length;
  $("#task-subtitle").textContent = current === "all" ? "По всем проектам" : state.projects.find((p) => p.id === Number(current))?.name || "Проект";
  if (!tasks.length) {
    $("#task-rows").innerHTML = '<tr class="empty-row"><td colspan="6">Задач пока нет. Нажмите «Добавить задачу», чтобы создать первую.</td></tr>';
    return;
  }
  $("#task-rows").innerHTML = tasks.map((task) => {
    const project = state.projects.find((p) => p.id === task.project_id);
    const user = state.users.find((u) => u.id === task.user_id);
    const name = user?.name || "Не назначен";
    return `<tr>
      <td><span class="task-name">${escapeHtml(task.title)}</span><span class="task-description">${escapeHtml(task.description || "Без описания")}</span></td>
      <td>${escapeHtml(project?.name || "—")}</td>
      <td><span class="assignee"><span class="assignee-circle">${escapeHtml(name.slice(0, 1).toUpperCase())}</span>${escapeHtml(name)}</span></td>
      <td class="${isOverdue(task) ? "overdue" : ""}">${escapeHtml(formatDate(task.deadline))}</td>
      <td>${badge(task.status)}</td>
      <td><button class="icon-btn" data-action="edit-task" data-id="${task.id}" aria-label="Изменить задачу" title="Редактировать">✎</button><button class="icon-btn" data-action="delete-task" data-id="${task.id}" aria-label="Удалить задачу" title="Удалить">✕</button></td>
    </tr>`;
  }).join("");
}

function openProject(project = null) {
  const form = $("#project-form");
  form.reset();
  form.elements.id.value = project?.id || "";
  form.elements.name.value = project?.name || "";
  form.elements.description.value = project?.description || "";
  $("#project-dialog-title").textContent = project ? "Редактировать проект" : "Новый проект";
  $("#project-dialog").showModal();
}

function openTask(task = null) {
  if (!state.projects.length) {
    toast("Сначала создайте проект", true);
    return;
  }
  const form = $("#task-form");
  form.reset();
  form.elements.project_id.innerHTML = state.projects.map((p) => `<option value="${p.id}">${escapeHtml(p.name)}</option>`).join("");
  form.elements.user_id.innerHTML = '<option value="">Не назначен</option>' + state.users.map((u) => `<option value="${u.id}">${escapeHtml(u.name)}</option>`).join("");
  form.elements.id.value = task?.id || "";
  form.elements.title.value = task?.title || "";
  form.elements.description.value = task?.description || "";
  form.elements.status.value = task?.status || "В работе";
  form.elements.project_id.value = task?.project_id || ($("#task-project-filter").value !== "all" ? $("#task-project-filter").value : state.projects[0].id);
  form.elements.user_id.value = task?.user_id || "";
  form.elements.deadline.value = task?.deadline?.slice(0, 16) || "";
  $("#task-dialog-title").textContent = task ? "Редактировать задачу" : "Новая задача";
  $("#task-dialog").showModal();
}

function openUsers() {
  $("#user-form").reset();
  $("#users-list").innerHTML = state.users.length ? state.users.map((user) =>
    `<div class="user-entry"><b>${escapeHtml(user.name)}</b><small>${escapeHtml(user.role)}</small></div>`
  ).join("") : '<p class="subtitle">Пока нет участников. Добавьте первого ниже.</p>';
  $("#user-dialog").showModal();
}

async function handleAction(action, id) {
  if (action === "new-project") return openProject();
  if (action === "edit-project") return openProject(state.projects.find((p) => p.id === id));
  if (action === "edit-task") return openTask(state.tasks.find((t) => t.id === id));
  if (action === "view-tasks") {
    $("#task-project-filter").value = String(id);
    renderTasks();
    $("#tasks-section").scrollIntoView({ behavior: "smooth" });
    return;
  }
  if (action === "delete-project") {
    if (!confirm("Удалить проект и все его задачи?")) return;
    await api(`/api/projects/${id}`, { method: "DELETE" });
    toast("Проект удалён");
  } else if (action === "delete-task") {
    if (!confirm("Удалить задачу?")) return;
    await api(`/api/tasks/${id}`, { method: "DELETE" });
    toast("Задача удалена");
  }
  await loadData();
}

document.addEventListener("click", async (event) => {
  const close = event.target.closest("[data-close]");
  if (close) { $("#" + close.dataset.close).close(); return; }
  const target = event.target.closest("[data-action]");
  if (!target) return;
  try { await handleAction(target.dataset.action, Number(target.dataset.id)); }
  catch (error) { toast(error.message, true); }
});

$("#add-project").addEventListener("click", () => openProject());
$("#add-task").addEventListener("click", () => openTask());
$("#side-users").addEventListener("click", openUsers);
$("#search-projects").addEventListener("input", renderProjects);
$("#filter-status").addEventListener("change", renderProjects);
$("#task-project-filter").addEventListener("change", renderTasks);

$("#project-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const id = form.elements.id.value;
  try {
    await api(id ? `/api/projects/${id}` : "/api/projects/", {
      method: id ? "PUT" : "POST",
      body: JSON.stringify({ name: form.elements.name.value.trim(), description: form.elements.description.value.trim() || null }),
    });
    $("#project-dialog").close();
    await loadData();
    toast(id ? "Проект изменён" : "Проект создан");
  } catch (error) { toast(error.message, true); }
});

$("#task-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const id = form.elements.id.value;
  try {
    await api(id ? `/api/tasks/${id}` : "/api/tasks/", {
      method: id ? "PUT" : "POST",
      body: JSON.stringify({
        title: form.elements.title.value.trim(),
        description: form.elements.description.value.trim() || null,
        status: form.elements.status.value,
        deadline: form.elements.deadline.value || null,
        project_id: Number(form.elements.project_id.value),
        user_id: form.elements.user_id.value ? Number(form.elements.user_id.value) : null,
      }),
    });
    $("#task-dialog").close();
    await loadData();
    toast(id ? "Задача изменена" : "Задача создана");
  } catch (error) { toast(error.message, true); }
});

$("#user-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  try {
    await api("/api/users/", {
      method: "POST",
      body: JSON.stringify({ name: form.elements.name.value.trim(), role: form.elements.role.value.trim() }),
    });
    await loadData();
    openUsers();
    toast("Участник добавлен");
  } catch (error) { toast(error.message, true); }
});

$("#year").textContent = new Date().getFullYear();
loadData().catch(() => toast("Не удалось загрузить данные. Проверьте сервер.", true));
