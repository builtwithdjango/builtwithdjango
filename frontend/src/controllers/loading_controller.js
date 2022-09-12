import { Controller } from "@hotwired/stimulus";

export default class extends Controller {
    static targets = [ "button", "loader" ];

    load() {
      this.loaderTarget.classList.replace('hidden', 'block');
      this.buttonTarget.classList.replace('bg-green-500', 'bg-green-200');
      this.buttonTarget.classList.remove('hover:bg-green-300');
      this.buttonTarget.disabled = true;
      document.form.submit();
    }
}
