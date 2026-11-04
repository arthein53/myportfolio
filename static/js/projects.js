(() => {
  const SEARCH_DEBOUNCE_DELAY = 300;

  document.addEventListener("DOMContentLoaded", () => {
    const page = document.querySelector("[data-projects-page]");
    if (!page) return;

    const projectsEndpoint = page.dataset.projectsEndpoint;
    const detailUrlTemplate = page.dataset.projectDetailTemplate;
    const starUrlTemplate = page.dataset.starUrlTemplate;
    const csrfToken = page.dataset.csrfToken;
    const isSuperuser = page.dataset.isSuperuser === "true";
    const isAuthenticated = page.dataset.isAuthenticated === "true";
    const loadingState = document.getElementById("projects-loading");
    const errorState = document.getElementById("projects-error");
    const emptyState = document.getElementById("projects-empty");
    const grid = document.getElementById("project-grid");
    const searchForm = document.getElementById("project-search-form");
    const searchInput = document.getElementById("project-search");
    const projectForm = document.getElementById("project-form");
    let projectsAbortController;
    let searchDebounceTimer;

    const displayPageSection = ({ showLoading = false, showError = false, showEmpty = false, showGrid = false }) => {
      loadingState.classList.toggle("hide", !showLoading);
      errorState.classList.toggle("hide", !showError);
      emptyState.classList.toggle("hide", !showEmpty);
      grid.classList.toggle("hide", !showGrid);
    };

    const createElement = (tagName, className, text) => {
      const element = document.createElement(tagName);
      if (className) element.className = className;
      if (text !== undefined) element.textContent = text;
      return element;
    };

    const safeUrl = (value) => {
      try {
        const url = new URL(value, window.location.origin);
        return ["http:", "https:"].includes(url.protocol) ? url.href : "#";
      } catch {
        return "#";
      }
    };

    const getCookie = (name) => {
      const prefix = `${name}=`;
      const cookie = document.cookie.split(";").map((value) => value.trim()).find((value) => value.startsWith(prefix));
      return cookie ? decodeURIComponent(cookie.slice(prefix.length)) : csrfToken;
    };

    const getProjectUrl = (template, projectId) => template.replace("/0/", `/${projectId}/`);

    const apiErrorMessage = (data, status) => {
      const messages = Object.values(data).flat().filter((value) => typeof value === "string");
      return messages.join(" ") || `Request failed (HTTP ${status}).`;
    };

    const writeProject = async (url, method, payload) => {
      const response = await fetch(url, {
        method,
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: payload === undefined ? undefined : JSON.stringify(payload),
      });
      if (response.status === 204) return null;
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(apiErrorMessage(data, response.status));
      return data;
    };

    const buildProjectCardElement = (project, index) => {
      const listItem = document.createElement("li");
      const article = createElement("article", "project");
      article.id = `project-${project.id}`;
      article.append(createElement("p", "project-number", String(index + 1).padStart(2, "0")));

      const content = createElement("div", "project-content");
      content.append(createElement("h2", "", project.title));
      content.append(createElement("p", "", project.description));
      if (Array.isArray(project.tags) && project.tags.length) {
        const tagList = createElement("ul", "project-tags");
        project.tags.forEach((tag) => tagList.append(createElement("li", "", tag)));
        content.append(tagList);
      }
      article.append(content);

      const meta = createElement("div", "project-meta");
      meta.append(createElement("p", "", project.period));
      meta.append(createElement("p", "", project.organization));
      const links = Array.isArray(project.links) && project.links.length ? project.links : [{ label: project.link_label, url: project.link_url }];
      links.forEach(({ label, url }) => {
        const link = createElement("a", "", `${label} ↗`);
        link.href = safeUrl(url);
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        meta.append(link);
      });

      if (isAuthenticated) {
        const starButton = createElement("button", `star-button${project.is_starred ? " is-starred" : ""}`);
        starButton.type = "button";
        starButton.dataset.action = "star";
        starButton.dataset.projectId = project.id;
        starButton.title = project.star_count ? `Starred by ${project.starred_by_names}` : "Be the first to star this project";
        starButton.append(createElement("span", "star-icon", project.is_starred ? "★" : "☆"));
        starButton.append(createElement("span", "star-count", String(project.star_count)));
        meta.append(starButton);
      } else {
        const loginLink = createElement("a", "star-button", `☆ ${project.star_count}`);
        loginLink.href = "/login/";
        loginLink.title = "Login to star this project";
        meta.append(loginLink);
      }

      if (isSuperuser) {
        const deleteButton = createElement("button", "button button-danger", "Delete");
        deleteButton.type = "button";
        deleteButton.dataset.action = "delete";
        deleteButton.dataset.projectId = project.id;
        meta.append(deleteButton);
      }

      article.append(meta);
      listItem.append(article);
      return listItem;
    };

    const renderProjects = (projects) => grid.replaceChildren(...projects.map(buildProjectCardElement));

    const fetchProjects = async (searchQuery = "") => {
      if (projectsAbortController) projectsAbortController.abort();
      projectsAbortController = new AbortController();
      const url = new URL(projectsEndpoint, window.location.origin);
      if (searchQuery) url.searchParams.set("title", searchQuery);

      try {
        displayPageSection({ showLoading: true });
        const response = await fetch(url, { headers: { Accept: "application/json" }, signal: projectsAbortController.signal });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const projects = await response.json();
        history.replaceState({}, "", `${window.location.pathname}${url.search}`);
        renderProjects(projects);
        displayPageSection({ showGrid: projects.length > 0, showEmpty: projects.length === 0 });
      } catch (error) {
        if (error.name === "AbortError") return;
        console.error("Error loading projects:", error);
        displayPageSection({ showError: true });
      }
    };

    const closeProjectModal = () => {
      const modal = document.getElementById("add-project-modal");
      if (modal?.matches(":popover-open")) modal.hidePopover();
    };

    if (projectForm) {
      projectForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const submitButton = projectForm.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        try {
          const fields = new FormData(projectForm);
          const payload = {
            title: fields.get("title"),
            description: fields.get("description"),
            period: fields.get("period"),
            organization: fields.get("organization"),
            link_label: fields.get("link_label"),
            link_url: fields.get("link_url"),
            tags: String(fields.get("tags") || "").split(",").map((tag) => tag.trim()).filter(Boolean),
            order: Number(fields.get("order") || 0),
            write_secret: fields.get("write_secret"),
          };
          await writeProject(projectsEndpoint, "POST", payload);
          projectForm.reset();
          closeProjectModal();
          showToast("Project added", "Project created.", "success");
          await fetchProjects(searchInput.value.trim());
        } catch (error) {
          showToast("Could not add project", error.message, "error");
        } finally {
          submitButton.disabled = false;
        }
      });
    }

    grid.addEventListener("click", async (event) => {
      const button = event.target.closest("button[data-action]");
      if (!button || button.disabled) return;
      const { action, projectId } = button.dataset;
      if (action === "delete" && !window.confirm("Delete this project?")) return;
      const writeSecret = action === "delete" ? window.prompt("Enter the project write code to delete this project:") : undefined;
      if (action === "delete" && writeSecret === null) return;

      button.disabled = true;
      try {
        const endpoint = action === "star" ? getProjectUrl(starUrlTemplate, projectId) : getProjectUrl(detailUrlTemplate, projectId);
        await writeProject(endpoint, action === "star" ? "POST" : "DELETE", action === "delete" ? { write_secret: writeSecret } : undefined);
        showToast("Success", action === "star" ? "Star updated." : "Project deleted.", "success");
        await fetchProjects(searchInput.value.trim());
      } catch (error) {
        showToast("Request failed", error.message, "error");
      } finally {
        button.disabled = false;
      }
    });

    searchInput.addEventListener("input", () => {
      clearTimeout(searchDebounceTimer);
      searchDebounceTimer = setTimeout(() => fetchProjects(searchInput.value.trim()), SEARCH_DEBOUNCE_DELAY);
    });
    searchForm.addEventListener("submit", (event) => {
      event.preventDefault();
      clearTimeout(searchDebounceTimer);
      fetchProjects(searchInput.value.trim());
    });

    fetchProjects(searchInput.value.trim());
  });
})();
