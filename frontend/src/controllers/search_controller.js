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
                result.classList.add("bg-gray-50");
                result.scrollIntoView({ block: "nearest" });
            } else {
                result.classList.remove("bg-gray-50");
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
        } catch (error) {
            console.error("Search error:", error);
            this.hideResults();
        }
    }

    showResults(results) {
        if (!results.length) {
            this.resultsTarget.innerHTML = `
                <div class="p-4 text-sm text-gray-500">
                    No projects found
                </div>
            `;
            this.resultsTarget.classList.remove("hidden");
            return;
        }

        this.resultsTarget.innerHTML = results.map(result => `
            <a href="/projects/${result.slug}"
               class="flex flex-col p-4 border-b border-gray-100 hover:bg-gray-50 last:border-b-0">
                <div class="font-medium text-gray-900">${result.title}</div>
                <div class="text-sm text-gray-500">${result.short_description}</div>
            </a>
        `).join("");

        this.resultsTarget.classList.remove("hidden");
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
}
