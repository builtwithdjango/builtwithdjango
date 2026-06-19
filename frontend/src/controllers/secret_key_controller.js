import { Controller } from "@hotwired/stimulus";

export default class extends Controller {
    static targets = [ "output", "copyButton", "generateButton", "status" ];
    static values = { url: String };

    async generate() {
        if (!this.urlValue) {
            this.setStatus("Secret key generation is not configured. Try again later.", true);
            return;
        }

        this.setGenerating(true);
        this.setStatus("Generating a new secret key...");

        try {
            const response = await fetch(this.urlValue, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({}),
            });

            if (!response.ok) {
                throw new Error(`Request failed with status ${response.status}`);
            }

            const data = await response.json();
            if (!data.secret_key) {
                throw new Error("The server did not return a secret key");
            }

            this.outputTarget.value = data.secret_key;
            this.copyButtonTarget.disabled = false;
            this.resetCopyButton();
            this.setStatus("Secret key generated. Copy it before leaving this page.");
            this.capture('django secret generated');
        } catch (error) {
            this.outputTarget.value = "";
            this.copyButtonTarget.disabled = true;
            this.setStatus("Could not generate a secret key. Check your connection and try again.", true);
            this.capture('django secret generation failed', {
                error: error.message
            });
        } finally {
            this.setGenerating(false);
        }
    }

    async copy() {
        if (!this.outputTarget.value) {
            this.setStatus("Generate a secret key before copying.", true);
            return;
        }

        try {
            await this.copyText(this.outputTarget.value);
        } catch (error) {
            this.setStatus("Could not copy automatically. Select the key and copy it manually.", true);
            this.capture('django secret copy failed', {
                error: error.message
            });
            return;
        }

        this.copyButtonTarget.textContent = "Copied";
        this.setStatus("Secret key copied.");
        this.capture('django secret copied');
    }

    resetCopyButton() {
        this.copyButtonTarget.textContent = "Copy";
    }

    setGenerating(isGenerating) {
        this.generateButtonTarget.disabled = isGenerating;
        this.generateButtonTarget.textContent = isGenerating ? "Generating..." : "Generate Secret Key";
    }

    setStatus(message, isError = false) {
        this.statusTarget.textContent = message;
        this.statusTarget.classList.toggle("bw-muted", !isError);
        this.statusTarget.classList.toggle("bw-status-error", isError);
    }

    async copyText(value) {
        if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(value);
            return;
        }

        const textarea = document.createElement("textarea");
        textarea.value = value;
        textarea.setAttribute("readonly", "");
        textarea.style.position = "fixed";
        textarea.style.top = "-9999px";
        document.body.appendChild(textarea);
        textarea.select();

        try {
            const copied = document.execCommand("copy");
            if (!copied) {
                throw new Error("Copy command was rejected");
            }
        } finally {
            textarea.remove();
        }
    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    capture(eventName, properties = {}) {
        if (window.bwdTrack) {
            window.bwdTrack(eventName, properties);
        }
    }
}
