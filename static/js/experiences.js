(() => {
  const SEARCH_DEBOUNCE_DELAY = 300;
  const UUID_PLACEHOLDER = "00000000-0000-0000-0000-000000000000";

  document.addEventListener("DOMContentLoaded", () => {
    const page = document.querySelector("[data-experiences-page]");
    if (!page) return;

    const endpoint = page.dataset.experiencesEndpoint;
    const detailTemplate = page.dataset.experienceDetailTemplate;
    const starTemplate = page.dataset.starUrlTemplate;
    const staticUrl = page.dataset.staticUrl;
    const csrfToken = page.dataset.csrfToken;
    const isSuperuser = page.dataset.isSuperuser === "true";
    const canEdit = page.dataset.canEdit === "true";
    const isAuthenticated = page.dataset.isAuthenticated === "true";
    const grid = document.getElementById("experience-grid");
    const loadingState = document.getElementById("experiences-loading");
    const errorState = document.getElementById("experiences-error");
    const emptyState = document.getElementById("experiences-empty");
    const searchForm = document.getElementById("experience-search-form");
    const searchInput = document.getElementById("experience-search");
    const experienceForm = document.getElementById("experience-form");
    const formModal = document.getElementById("experience-form-modal");
    const formTitle = document.getElementById("experience-form-title");
    const formSubmit = document.getElementById("experience-form-submit");
    const writeSecretGroup = document.querySelector(".experience-write-secret");
    const deleteModal = document.getElementById("experience-delete-modal");
    const deleteForm = document.getElementById("experience-delete-form");
    const experiencesById = new Map();
    let currentExperienceId = null;
    let pendingDeleteId = null;
    let requestController;
    let searchTimer;

    const createElement = (tagName, className, text) => {
      const element = document.createElement(tagName);
      if (className) element.className = className;
      if (text !== undefined) element.textContent = text;
      return element;
    };

    const displayPageSection = ({ loading = false, error = false, empty = false, content = false }) => {
      loadingState.classList.toggle("hide", !loading);
      errorState.classList.toggle("hide", !error);
      emptyState.classList.toggle("hide", !empty);
      grid.classList.toggle("hide", !content);
    };

    const getCookie = (name) => {
      const prefix = `${name}=`;
      const cookie = document.cookie
        .split(";")
        .map((value) => value.trim())
        .find((value) => value.startsWith(prefix));
      return cookie ? decodeURIComponent(cookie.slice(prefix.length)) : csrfToken;
    };

    const itemUrl = (template, experienceId) => template.replace(UUID_PLACEHOLDER, experienceId);

    const errorMessages = (value) => {
      if (typeof value === "string") return [value];
      if (Array.isArray(value)) return value.flatMap(errorMessages);
      if (value && typeof value === "object") return Object.values(value).flatMap(errorMessages);
      return [];
    };

    const apiRequest = async (url, method = "GET", payload) => {
      const response = await fetch(url, {
        method,
        headers: {
          Accept: "application/json",
          ...(method === "GET" ? {} : {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          }),
        },
        body: payload === undefined ? undefined : JSON.stringify(payload),
      });
      if (response.status === 204) return null;
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        const message = errorMessages(data).join(" ") || `Request failed (HTTP ${response.status}).`;
        throw new Error(message);
      }
      return data;
    };

    const thumbnailUrl = (thumbnail) => {
      if (!thumbnail) return "";
      try {
        const parsed = new URL(thumbnail, window.location.origin);
        if (["http:", "https:"].includes(parsed.protocol) && /^https?:/i.test(thumbnail)) {
          return parsed.href;
        }
      } catch {
        return "";
      }
      if (thumbnail.includes("..") || thumbnail.startsWith("/")) return "";
      return `${staticUrl}${thumbnail.replace(/^\/+/, "")}`;
    };

    const addActionButton = (container, text, action, experienceId, className = "button") => {
      const button = createElement("button", className, text);
      button.type = "button";
      button.dataset.action = action;
      button.dataset.experienceId = experienceId;
      container.append(button);
    };

    const buildExperienceCard = (experience) => {
      const article = createElement("article", "experience-card");
      article.id = `experience-${experience.id}`;

      const imageUrl = thumbnailUrl(experience.thumbnail);
      if (imageUrl) {
        const image = createElement("img", "experience-thumbnail");
        image.src = imageUrl;
        image.alt = `Thumbnail for ${experience.organization || experience.title}`;
        image.loading = "lazy";
        article.append(image);
      } else {
        const placeholder = createElement("div", "experience-thumbnail experience-thumbnail-placeholder");
        placeholder.append(createElement("span", "", "Experience"));
        article.append(placeholder);
      }

      const content = createElement("div", "experience-card-content");
      content.append(createElement("span", "experience-category", experience.category_display));
      content.append(createElement("h2", "", experience.organization || experience.title));
      if (experience.position) content.append(createElement("p", "experience-position", experience.position));
      if (experience.period) content.append(createElement("p", "experience-period", experience.period));
      content.append(createElement("p", "experience-description", experience.description));
      content.append(createElement("p", "experience-status", experience.is_ongoing ? "Ongoing" : "Finished"));

      const actions = createElement("div", "experience-actions");
      if (isAuthenticated) {
        const starButton = createElement("button", `star-button${experience.is_starred ? " is-starred" : ""}`);
        starButton.type = "button";
        starButton.dataset.action = "star";
        starButton.dataset.experienceId = experience.id;
        starButton.title = `${experience.star_count} stars`;
        starButton.append(createElement("span", "star-icon", experience.is_starred ? "★" : "☆"));
        starButton.append(createElement("span", "star-count", String(experience.star_count)));
        actions.append(starButton);
      } else {
        const loginLink = createElement("a", "star-button", `☆ ${experience.star_count}`);
        loginLink.href = `/login/?next=${encodeURIComponent(window.location.pathname)}`;
        loginLink.title = "Login to star this experience";
        actions.append(loginLink);
      }
      if (canEdit) addActionButton(actions, "Edit", "edit", experience.id, "button button-secondary");
      if (isSuperuser) addActionButton(actions, "Delete", "delete", experience.id, "button button-danger");
      content.append(actions);
      article.append(content);
      return article;
    };

    const renderExperiences = (experiences) => {
      experiencesById.clear();
      experiences.forEach((experience) => experiencesById.set(experience.id, experience));
      grid.replaceChildren(...experiences.map(buildExperienceCard));
    };

    const fetchExperiences = async (query = "") => {
      if (requestController) requestController.abort();
      requestController = new AbortController();
      const url = new URL(endpoint, window.location.origin);
      if (query) url.searchParams.set("title", query);

      try {
        displayPageSection({ loading: true });
        const response = await fetch(url, {
          headers: { Accept: "application/json" },
          signal: requestController.signal,
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const experiences = await response.json();
        history.replaceState({}, "", `${window.location.pathname}${url.search}`);
        renderExperiences(experiences);
        displayPageSection({ content: experiences.length > 0, empty: experiences.length === 0 });
      } catch (error) {
        if (error.name === "AbortError") return;
        console.error("Error loading experiences:", error);
        displayPageSection({ error: true });
      }
    };

    const setFormMode = (experience = null) => {
      if (!experienceForm) return;
      currentExperienceId = experience?.id || null;
      experienceForm.reset();
      formTitle.textContent = experience ? "Edit experience" : "Add experience";
      formSubmit.textContent = experience ? "Save changes" : "Add experience";
      writeSecretGroup?.classList.toggle("hide", Boolean(experience));
      if (!experience) return;
      ["title", "organization", "position", "period", "description", "category", "thumbnail"].forEach((fieldName) => {
        const input = experienceForm.elements.namedItem(fieldName);
        if (input) input.value = experience[fieldName] || "";
      });
      const endedAtInput = experienceForm.elements.namedItem("ended_at");
      if (endedAtInput) {
        endedAtInput.value = experience.ended_at
          ? new Date(experience.ended_at).toISOString().slice(0, 16)
          : "";
      }
    };

    document.querySelector(".experience-add-button")?.addEventListener("click", () => setFormMode());

    experienceForm?.addEventListener("submit", async (event) => {
      event.preventDefault();
      const submitButton = experienceForm.querySelector('button[type="submit"]');
      const fields = new FormData(experienceForm);
      const payload = {
        title: fields.get("title"),
        organization: fields.get("organization"),
        position: fields.get("position"),
        period: fields.get("period"),
        description: fields.get("description"),
        category: fields.get("category"),
        thumbnail: fields.get("thumbnail"),
        ended_at: fields.get("ended_at") || null,
      };
      if (!currentExperienceId) payload.write_secret = fields.get("write_secret");

      submitButton.disabled = true;
      try {
        const url = currentExperienceId ? itemUrl(detailTemplate, currentExperienceId) : endpoint;
        await apiRequest(url, currentExperienceId ? "PATCH" : "POST", payload);
        if (formModal?.matches(":popover-open")) formModal.hidePopover();
        showToast(
          currentExperienceId ? "Experience updated" : "Experience added",
          currentExperienceId ? "Changes saved." : "Experience created.",
          "success",
        );
        setFormMode();
        await fetchExperiences(searchInput.value.trim());
      } catch (error) {
        showToast("Could not save experience", error.message, "error");
      } finally {
        submitButton.disabled = false;
      }
    });

    grid.addEventListener("click", async (event) => {
      const button = event.target.closest("button[data-action]");
      if (!button || button.disabled) return;
      const { action, experienceId } = button.dataset;

      if (action === "edit") {
        const experience = experiencesById.get(experienceId);
        if (!experience) return;
        setFormMode(experience);
        formModal?.showPopover();
        return;
      }
      if (action === "delete") {
        pendingDeleteId = experienceId;
        deleteForm?.reset();
        deleteModal?.showPopover();
        return;
      }

      button.disabled = true;
      try {
        await apiRequest(itemUrl(starTemplate, experienceId), "POST");
        showToast("Success", "Star updated.", "success");
        await fetchExperiences(searchInput.value.trim());
      } catch (error) {
        showToast("Request failed", error.message, "error");
      } finally {
        button.disabled = false;
      }
    });

    deleteForm?.addEventListener("submit", async (event) => {
      event.preventDefault();
      if (!pendingDeleteId) return;
      const submitButton = deleteForm.querySelector('button[type="submit"]');
      const writeSecret = new FormData(deleteForm).get("write_secret");
      submitButton.disabled = true;
      try {
        await apiRequest(
          itemUrl(detailTemplate, pendingDeleteId),
          "DELETE",
          { write_secret: writeSecret },
        );
        pendingDeleteId = null;
        deleteForm.reset();
        if (deleteModal?.matches(":popover-open")) deleteModal.hidePopover();
        showToast("Experience deleted", "The experience was removed.", "success");
        await fetchExperiences(searchInput.value.trim());
      } catch (error) {
        showToast("Could not delete experience", error.message, "error");
      } finally {
        submitButton.disabled = false;
      }
    });

    searchInput.addEventListener("input", () => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => fetchExperiences(searchInput.value.trim()), SEARCH_DEBOUNCE_DELAY);
    });
    searchForm.addEventListener("submit", (event) => {
      event.preventDefault();
      clearTimeout(searchTimer);
      fetchExperiences(searchInput.value.trim());
    });

    fetchExperiences(searchInput.value.trim());
  });
})();
