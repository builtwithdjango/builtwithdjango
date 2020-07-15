import { Controller } from "stimulus"

export default class extends Controller {
    static targets = [ "nav" ]

    shownav() {
        const element = this.navTarget
        if (element.classList.contains('hidden')) {
            element.classList.remove("hidden")
        } else {
            element.classList.add("hidden");
        }
    }
}