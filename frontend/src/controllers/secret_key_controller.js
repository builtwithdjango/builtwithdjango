import { Controller } from "@hotwired/stimulus";

export default class extends Controller {
    static targets = [ "output", "copyButton" ];
    static values = { url: String };

    generate() {
        if (!this.urlValue) {
            console.error('URL is undefined');
            this.outputTarget.value = 'Error: URL is not set';
            return;
        }

        fetch(this.urlValue, {
            method: 'POST',
            headers: {
                'X-CSRFToken': this.getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({}),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            this.outputTarget.value = data.secret_key;
            this.resetCopyButton();  // Reset the copy button when new secret is generated
        })
        .catch(error => {
            console.error('Error:', error);
            this.outputTarget.value = 'An error occurred: ' + error.message;
        });
    }

    copy() {
        navigator.clipboard.writeText(this.outputTarget.value);
        this.copyButtonTarget.classList.replace("bg-green-600", "bg-blue-600");
        this.copyButtonTarget.textContent = "Copied";
    }

    resetCopyButton() {
        this.copyButtonTarget.classList.replace("bg-blue-600", "bg-green-600");
        this.copyButtonTarget.textContent = "Copy";
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
}
