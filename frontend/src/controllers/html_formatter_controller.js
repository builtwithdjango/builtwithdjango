import { Controller } from "@hotwired/stimulus";

export default class extends Controller {
  static targets = [ "input", "result", "submitButton", "copyButton", "status" ];

  formatHTML() {
    const input = this.inputTarget.value.trim();
    if (!input) {
      this.setError('Paste a Django template before formatting.');
      return;
    }

    this.setLoading(true);
    this.setStatus('Formatting template...');

    const formData = new FormData();
    formData.append('html_string', input);

    fetch('/tools/api/format-html/', {
      method: 'POST',
      body: formData,
    })
    .then(async response => {
      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.error || `Request failed with status ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      if (data.formatted_html) {
        this.resultTarget.value = data.formatted_html;
        this.copyButtonTarget.disabled = false;
        this.resetCopyButton();
        this.setStatus('Formatted HTML is ready.');
        this.capture('html formatted', {
          input_length: input.length,
          output_length: data.formatted_html.length
        });
      } else if (data.error) {
        this.setError(data.error);
        this.capture('html formatter failed', {
          input_length: input.length,
          error: data.error
        });
      }
    })
    .catch(error => {
      this.setError(error.message || 'Could not format HTML. Check your connection and try again.');
      this.capture('html formatter failed', {
        input_length: input.length,
        error: error.message
      });
    })
    .finally(() => {
      this.setLoading(false);
    });
  }

  async copy() {
    if (!this.resultTarget.value) {
      this.setError('Format HTML before copying.');
      return;
    }

    try {
      await this.copyText(this.resultTarget.value);
    } catch (error) {
      this.setError('Could not copy automatically. Select the result and copy it manually.');
      this.capture('formatted html copy failed', {
        error: error.message
      });
      return;
    }

    this.copyButtonTarget.textContent = "Copied!";
    this.setStatus('Formatted HTML copied.');
    this.capture('formatted html copied', {
      output_length: this.resultTarget.value.length
    });
    setTimeout(() => this.resetCopyButton(), 2000);
  }

  resetCopyButton() {
    this.copyButtonTarget.textContent = "Copy";
  }

  setLoading(isLoading) {
    this.submitButtonTarget.disabled = isLoading;
    this.submitButtonTarget.textContent = isLoading ? 'Formatting...' : 'Format HTML';
  }

  setStatus(message) {
    this.statusTarget.textContent = message;
    this.statusTarget.classList.add('bw-muted');
    this.statusTarget.classList.remove('bw-status-error');
  }

  setError(message) {
    this.resultTarget.value = '';
    this.copyButtonTarget.disabled = true;
    this.statusTarget.textContent = message;
    this.statusTarget.classList.remove('bw-muted');
    this.statusTarget.classList.add('bw-status-error');
  }

  async copyText(value) {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(value);
      return;
    }

    const textarea = document.createElement('textarea');
    textarea.value = value;
    textarea.setAttribute('readonly', '');
    textarea.style.position = 'fixed';
    textarea.style.top = '-9999px';
    document.body.appendChild(textarea);
    textarea.select();

    try {
      const copied = document.execCommand('copy');
      if (!copied) {
        throw new Error('Copy command was rejected');
      }
    } finally {
      textarea.remove();
    }
  }

  clearResult() {
    this.resultTarget.value = '';
    this.copyButtonTarget.disabled = true;
    this.setStatus('Result cleared.');
    this.capture('html formatter cleared');
  }

  capture(eventName, properties = {}) {
    if (window.bwdTrack) {
      window.bwdTrack(eventName, properties);
    }
  }
}
