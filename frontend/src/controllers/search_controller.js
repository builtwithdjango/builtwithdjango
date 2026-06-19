import { Controller } from "@hotwired/stimulus";

export default class extends Controller {
    static targets = ["input", "results"];
    static values = {
        url: String,
        debounce: { type: Number, default: 300 }
    };

    initialize() {
        this.debouncedSearch = this.debounce(this.search.bind(this), this.debounceValue);
        this.onClickOutside = this.onClickOutside.bind(this);
        this.handleKeyPress = this.handleKeyPress.bind(this);
        this.selectedIndex = -1;
        document.addEventListener("click", this.onClickOutside);
        document.addEventListener("keydown", this.handleKeyPress);
    }

    disconnect() {
        document.removeEventListener("click", this.onClickOutside);
        document.removeEventListener("keydown", this.handleKeyPress);
    }

    handleKeyPress(event) {
        // Focus search on '/' key press
        if (event.key === "/" && document.activeElement !== this.inputTarget) {
            event.preventDefault();
            this.inputTarget.focus();
            this.capture("search keyboard shortcut used");
            return;
        }

        // Handle arrow keys and enter only when results are visible
        if (this.resultsTarget.classList.contains("hidden")) {
            return;
        }

        const results = this.resultsTarget.querySelectorAll("a");
        if (!results.length) return;

        switch (event.key) {
            case "ArrowDown":
                event.preventDefault();
                this.selectedIndex = Math.min(this.selectedIndex + 1, results.length - 1);
                this.updateSelection(results);
                break;

            case "ArrowUp":
                event.preventDefault();
                this.selectedIndex = Math.max(this.selectedIndex - 1, -1);
                this.updateSelection(results);
                break;

            case "Enter":
                event.preventDefault();
                if (this.selectedIndex >= 0) {
                    results[this.selectedIndex].click();
                }
                break;

            case "Escape":
                event.preventDefault();
                this.hideResults();
                break;
        }
    }

    updateSelection(results) {
        results.forEach((result, index) => {
            if (index === this.selectedIndex) {
                result.classList.add("bw-search-result--active");
                result.scrollIntoView({ block: "nearest" });
            } else {
                result.classList.remove("bw-search-result--active");
            }
        });
    }

    onClickOutside(event) {
        if (!this.element.contains(event.target)) {
            this.hideResults();
        }
    }

    onInput(event) {
        const query = event.target.value.trim();
        if (query.length < 1) {
            this.hideResults();
            return;
        }
        this.selectedIndex = -1;
        this.capture("project search typed", {
            query_length: query.length
        });
        this.debouncedSearch(query);
    }

    async search(query) {
        try {
            const response = await fetch(`${this.urlValue}?q=${encodeURIComponent(query)}`, {
                headers: {
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            this.showResults(data.slice(0, 3));
            this.capture("project search results shown", {
                query,
                query_length: query.length,
                result_count: data.length,
                visible_result_count: Math.min(data.length, 3),
                has_results: data.length > 0
            });
        } catch (error) {
            this.capture("project search failed", {
                query_length: query.length,
                error: error.message
            });
            this.hideResults();
        }
    }

    showResults(results) {
        if (!results.length) {
            const emptyState = document.createElement("div");
            emptyState.className = "bw-search-empty";
            emptyState.textContent = "No projects found";
            this.resultsTarget.replaceChildren(emptyState);
            this.resultsTarget.classList.remove("hidden");
            return;
        }

        this.resultsTarget.replaceChildren(...results.map(result => this.buildResultLink(result)));
        this.resultsTarget.classList.remove("hidden");
    }

    buildResultLink(result) {
        const link = document.createElement("a");
        link.href = `/projects/${encodeURIComponent(result.slug || "")}`;
        link.dataset.analyticsEvent = "project search result clicked";
        link.dataset.analyticsProjectId = String(result.id || "");
        link.dataset.analyticsProjectTitle = result.title || "";
        link.dataset.analyticsProjectSlug = result.slug || "";
        link.className = "bw-search-result";

        const title = document.createElement("div");
        title.className = "bw-search-result__title";
        title.textContent = result.title || "";

        const description = document.createElement("div");
        description.className = "bw-search-result__description";
        description.textContent = result.short_description || "";

        link.append(title, description);
        return link;
    }

    hideResults() {
        this.resultsTarget.classList.add("hidden");
        this.selectedIndex = -1;
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    capture(eventName, properties = {}) {
        if (window.bwdTrack) {
            window.bwdTrack(eventName, properties);
        }
    }
}
