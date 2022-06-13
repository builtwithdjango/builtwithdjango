import { Controller } from "@hotwired/stimulus";
import {enter, leave} from 'el-transition';

export default class extends Controller {
    static targets = [ "modal", "closeButton" ];

    initialize() {
      this.numOfOpens = 0;
    }

    openModal(event) {
      if(this.modalTarget.classList.contains('hidden') && this.numOfOpens === 0) {
        if (!event.toElement && !event.relatedTarget) {
          setTimeout(() => {
            enter(this.modalTarget);
            this.numOfOpens++;
          }, 1000);
        }
      }
    }

    closeModal() {
        console.log("not hidden");
        leave(this.modalTarget);
    }
}
