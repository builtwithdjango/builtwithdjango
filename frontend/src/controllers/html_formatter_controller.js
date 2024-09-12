import { Controller } from "@hotwired/stimulus";

export default class extends Controller {
  static targets = [ "input", "result", "submitButton", "copyButton" ];

  formatHTML() {
    this.setLoading(true);

    const formData = new FormData();
    formData.append('html_string', this.inputTarget.value);

    fetch('/tools/api/format-html/', {
      method: 'POST',
      body: formData,
    })
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      if (data.formatted_html) {
        this.resultTarget.value = data.formatted_html;
        this.copyButtonTarget.classList.remove('hidden');
      } else if (data.error) {
        this.resultTarget.value = 'Error: ' + data.error;
        this.copyButtonTarget.classList.add('hidden');
      }
    })
    .catch(error => {
      this.resultTarget.value = 'Error: ' + error;
      this.copyButtonTarget.classList.add('hidden');
    })
    .finally(() => {
      this.setLoading(false);
    });
  }

  copy() {
    navigator.clipboard.writeText(this.resultTarget.value);
    this.copyButtonTarget.classList.replace("bg-blue-500", "bg-green-500");
    this.copyButtonTarget.textContent = "Copied!";
    setTimeout(() => this.resetCopyButton(), 2000);
  }

  resetCopyButton() {
    this.copyButtonTarget.classList.replace("bg-green-500", "bg-blue-500");
    this.copyButtonTarget.textContent = "Copy";
  }

  setLoading(isLoading) {
    this.submitButtonTarget.disabled = isLoading;
    this.submitButtonTarget.textContent = isLoading ? 'Formatting...' : 'Format HTML';
    this.submitButtonTarget.classList.toggle('opacity-50', isLoading);
    this.submitButtonTarget.classList.toggle('cursor-not-allowed', isLoading);
  }

  clearResult() {
    this.resultTarget.value = '';
    this.copyButtonTarget.classList.add('hidden');
  }
}
