(() => {
  const SEARCH_DEBOUNCE_DELAY = 300;

  document.addEventListener("DOMContentLoaded", () => {
    const page = document.querySelector("[data-projects-page]");
    if (!page) return;

    const projectsEndpoint = page.dataset.projectsEndpoint;
    const createProjectEndpoint = page.dataset.createProjectEndpoint;
    const starUrlTemplate = page.dataset.starUrlTemplate;
    const csrfToken = page.dataset.csrfToken;
    const isSuperuser = page.dataset.isSuperuser === "true";
    const loadingState = document.getElementById("projects-loading");
    const errorState = document.getElementById("projects-error");
    const emptyState = document.getElementById("projects-empty");
    const grid = document.getElementById("project-grid");
    const searchForm = document.getElementById("project-search-form");
    const searchInput = document.getElementById("project-search");
    const projectForm = document.getElementById("project-form");
    let projectsAbortController;
    let searchDebounceTimer;

    const displayPageSection = ({
      showLoading = false,
      showError = false,
      showEmpty = false,
      showGrid = false,
    }) => {
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

    const getStarUrl = (projectId) =>
      starUrlTemplate.replace("/0/star/", `/${projectId}/star/`);

    const buildProjectCardElement = (item, index) => {
      const { fields: project } = item;
      const listItem = document.createElement("li");
      const article = createElement("article", "project");
      article.id = `project-${item.pk}`;

      article.append(
        createElement(
          "p",
          "project-number",
          String(index + 1).padStart(2, "0"),
        ),
      );

      const content = createElement("div", "project-content");
      content.append(createElement("h2", "", project.title));
      content.append(createElement("p", "", project.description));

      const tags = Array.isArray(project.tags) ? project.tags : [];
      if (tags.length) {
        const tagList = createElement("ul", "project-tags");
        tags.forEach((tag) => tagList.append(createElement("li", "", tag)));
        content.append(tagList);
      }
      article.append(content);

      const meta = createElement("div", "project-meta");
      meta.append(createElement("p", "", project.period));
      meta.append(createElement("p", "", project.organization));

      const links =
        Array.isArray(project.links) && project.links.length
          ? project.links
          : [{ label: project.link_label, url: project.link_url }];
      links.forEach(({ label, url }) => {
        const link = createElement("a", "", `${label} ↗`);
        link.href = safeUrl(url);
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        meta.append(link);
      });

      const starForm = createElement("form", "star-form");
      starForm.method = "post";
      starForm.action = getStarUrl(item.pk);
      starForm.dataset.starForm = "";
      const starToken = document.createElement("input");
      starToken.type = "hidden";
      starToken.name = "csrfmiddlewaretoken";
      starToken.value = csrfToken;
      const returnTo = document.createElement("input");
      returnTo.type = "hidden";
      returnTo.name = "return_to";
      returnTo.value = "projects";
      const starButton = createElement(
        "button",
        `star-button${project.is_starred ? " is-starred" : ""}`,
      );
      starButton.type = "submit";
      starButton.title = project.star_count
        ? `Starred by ${project.starred_by_names}`
        : "Be the first to star this project";
      starButton.append(
        createElement("span", "star-icon", project.is_starred ? "★" : "☆"),
      );
      starButton.append(
        createElement("span", "star-count", String(project.star_count)),
      );
      starForm.append(starToken, returnTo, starButton);
      meta.append(starForm);

      article.append(meta);
      listItem.append(article);
      return listItem;
    };

    const renderProjects = (projects) => {
      grid.replaceChildren();
      projects.forEach((project, index) =>
        grid.append(buildProjectCardElement(project, index)),
      );
    };

    const fetchProjects = async (searchQuery = "") => {
      if (projectsAbortController) projectsAbortController.abort();
      projectsAbortController = new AbortController();
      const url = new URL(projectsEndpoint, window.location.origin);
      if (searchQuery) url.searchParams.set("title", searchQuery);

      try {
        displayPageSection({ showLoading: true });
        const response = await fetch(url, {
          headers: { Accept: "application/json" },
          signal: projectsAbortController.signal,
        });
        if (!response.ok) throw new Error("Failed to fetch projects.");

        const projects = await response.json();
        history.replaceState(
          {},
          "",
          `${window.location.pathname}${url.search}`,
        );
        if (!projects.length) {
          displayPageSection({ showEmpty: true });
          return;
        }

        renderProjects(projects);
        displayPageSection({ showGrid: true });
      } catch (error) {
        if (error.name === "AbortError") return;
        console.error("Error loading projects:", error);
        displayPageSection({ showError: true });
      }
    };

    const searchProjects = () => fetchProjects(searchInput.value.trim());

    searchInput.addEventListener("input", () => {
      clearTimeout(searchDebounceTimer);
      searchDebounceTimer = setTimeout(searchProjects, SEARCH_DEBOUNCE_DELAY);
    });

    searchForm.addEventListener("submit", (event) => {
      event.preventDefault();
      clearTimeout(searchDebounceTimer);
      searchProjects();
    });

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
          const response = await fetch(createProjectEndpoint, {
            method: "POST",
            headers: { Accept: "application/json" },
            body: new FormData(projectForm),
          });
          const result = await response.json().catch(() => ({}));

          if (!response.ok) {
            const errors = result.errors
              ? Object.values(result.errors)
                  .flat()
                  .map((error) => error.message)
              : [
                  result.message ||
                    `Request failed with status ${response.status}.`,
                ];
            showToast("Could not add project", errors.join(" "), "error");
            return;
          }

          projectForm.reset();
          closeProjectModal();
          showToast("Project added", result.message, "success");
          searchProjects();
        } catch (error) {
          console.error("Error adding project:", error);
          showToast(
            "Could not add project",
            "Unable to connect to the server.",
            "error",
          );
        } finally {
          submitButton.disabled = false;
        }
      });
    }

    grid.addEventListener("submit", async (event) => {
      const form = event.target.closest("[data-star-form]");
      if (!form) return;
      event.preventDefault();

      const button = form.querySelector(".star-button");
      const icon = form.querySelector(".star-icon");
      const count = form.querySelector(".star-count");
      if (button.disabled) return;
      button.disabled = true;

      try {
        const response = await fetch(form.action, {
          method: "POST",
          headers: { Accept: "application/json" },
          body: new FormData(form),
        });
        if (!response.ok) throw new Error("Unable to update star.");
        const result = await response.json();
        button.classList.toggle("is-starred", result.starred);
        icon.textContent = result.starred ? "★" : "☆";
        count.textContent = result.count;
        button.title = `${result.count} stars`;
      } catch (error) {
        console.error("Error updating star:", error);
        form.submit();
      } finally {
        button.disabled = false;
      }
    });

    if (!isSuperuser) {
      document.getElementById("add-project-modal")?.remove();
    }
    fetchProjects(searchInput.value.trim());
  });
})();
