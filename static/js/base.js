(() => {
    const root = document.documentElement;
    const mediaQuery = window.matchMedia("(prefers-color-scheme: light)");

    const isValidTheme = (value) => value === "light" || value === "dark";

    const getStoredTheme = () => {
        try {
            return localStorage.getItem("portfolio-theme");
        } catch {
            return null;
        }
    };

    const saveTheme = (theme) => {
        try {
            localStorage.setItem("portfolio-theme", theme);
        } catch {
            // ignore storage errors
        }
    };

    const applyTheme = (theme, persist = false) => {
        const normalizedTheme = isValidTheme(theme)
            ? theme
            : mediaQuery.matches
                ? "light"
                : "dark";

        root.dataset.theme = normalizedTheme;

        if (persist) {
            saveTheme(normalizedTheme);
        }
    };

    const resolveInitialTheme = () => {
        const savedTheme = getStoredTheme();
        return isValidTheme(savedTheme)
            ? savedTheme
            : mediaQuery.matches
                ? "light"
                : "dark";
    };

    applyTheme(resolveInitialTheme());

    document.addEventListener("DOMContentLoaded", () => {
        const toggle = document.querySelector(".theme-toggle");
        const menuToggle = document.querySelector(".menu-toggle");
        const primaryNav = document.querySelector("#primary-nav");
        const label = toggle?.querySelector(".theme-toggle-label");

        const updateThemeLabel = () => {
            if (!label) return;
            label.textContent = root.dataset.theme === "dark" ? "Light" : "Dark";
        };

        if (toggle) {
            updateThemeLabel();

            toggle.addEventListener("click", () => {
                const nextTheme = root.dataset.theme === "dark" ? "light" : "dark";
                applyTheme(nextTheme, true);
                updateThemeLabel();
            });
        }

        if (!getStoredTheme()) {
            mediaQuery.addEventListener("change", (event) => {
                applyTheme(event.matches ? "light" : "dark");
                updateThemeLabel();
            });
        }

        if (menuToggle && primaryNav) {
            const closeMenu = () => {
                primaryNav.classList.remove("is-open");
                menuToggle.classList.remove("is-open");
            };

            menuToggle.addEventListener("click", () => {
                const isOpen = primaryNav.classList.toggle("is-open");
                menuToggle.classList.toggle("is-open", isOpen);
            });

            primaryNav.querySelectorAll("a").forEach((link) => {
                link.addEventListener("click", closeMenu);
            });

            document.addEventListener("keydown", (event) => {
                if (event.key === "Escape") {
                    closeMenu();
                }
            });
        }

        const closePlayer = (item) => {
            if (!item) return;

            const listItem = item.closest("li");
            if (!listItem) return;

            const audio = listItem.querySelector("audio");
            if (audio) {
                audio.pause();
                audio.currentTime = 0;
            }

            const player = listItem.querySelector(".discography-player");
            if (player) {
                player.hidden = true;
            }

            item.classList.remove("is-player-open");
        };

        const openPlayer = (item) => {
            if (!item) return;

            if (item.classList.contains("is-player-open")) {
                closePlayer(item);
                return;
            }

            const currentOpen = document.querySelector(".discography-item.is-player-open");
            if (currentOpen && currentOpen !== item) {
                closePlayer(currentOpen);
            }

            const listItem = item.closest("li");
            if (!listItem) return;

            let player = listItem.querySelector(".discography-player");

            if (!player) {
                player = document.createElement("div");
                player.className = "discography-player";

                const audio = document.createElement("audio");
                audio.controls = true;
                audio.preload = "metadata";
                audio.src = item.dataset.audioSrc;

                player.append(audio);
                listItem.append(player);
            }

            player.hidden = false;
            item.classList.add("is-player-open");
        };

        document.querySelectorAll(".discography-item").forEach((item) => {
            item.addEventListener("click", (event) => {
                if (event.target.closest("a, audio, button")) return;
                openPlayer(item);
            });

            item.addEventListener("keydown", (event) => {
                if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    openPlayer(item);
                }
            });
        });

        document.querySelectorAll("[data-star-form]").forEach((form) => {
            form.addEventListener("submit", async (event) => {
                event.preventDefault();

                const button = form.querySelector(".star-button");
                const icon = form.querySelector(".star-icon");
                const count = form.querySelector(".star-count");

                if (!button || !icon || !count || button.disabled) return;

                button.disabled = true;

                try {
                    const response = await fetch(form.action, {
                        method: "POST",
                        body: new FormData(form),
                        headers: {
                            Accept: "application/json",
                        },
                    });

                    const contentType = response.headers.get("content-type") || "";
                    if (!contentType.includes("application/json")) {
                        window.location.assign(response.url);
                        return;
                    }

                    if (!response.ok) {
                        throw new Error("Unable to update star.");
                    }

                    const { starred, count: total } = await response.json();

                    button.classList.toggle("is-starred", starred);
                    icon.textContent = starred ? "★" : "☆";
                    count.textContent = total;
                    button.title = `${total} stars`;
                } catch {
                    form.submit();
                } finally {
                    button.disabled = false;
                }
            });
        });
    });
})();