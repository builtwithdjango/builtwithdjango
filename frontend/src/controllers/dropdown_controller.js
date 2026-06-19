import Dropdown from "stimulus-dropdown";

export default class extends Dropdown {
  connect() {
    super.connect();
    this.boundCloseOnEscape = this.closeOnEscape.bind(this);
    document.addEventListener("keydown", this.boundCloseOnEscape);
    this.setExpanded(false);
  }

  disconnect() {
    document.removeEventListener("keydown", this.boundCloseOnEscape);
    super.disconnect?.();
  }

  toggle(event) {
    super.toggle(event);
    window.requestAnimationFrame(() => {
      this.setExpanded(!this.menuTarget.classList.contains("hidden"));
    });
  }

  hide(event) {
    super.hide(event);
    if (!this.element.contains(event.target)) {
      this.setExpanded(false);
    }
  }

  closeOnEscape(event) {
    if (event.key !== "Escape" || this.menuTarget.classList.contains("hidden")) return;

    this.leave();
    this.setExpanded(false);
    this.triggerElement?.focus();
  }

  setExpanded(isExpanded) {
    this.triggerElement?.setAttribute("aria-expanded", isExpanded ? "true" : "false");
  }

  get triggerElement() {
    return this.element.querySelector("[aria-expanded]");
  }
}
