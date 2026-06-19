import { Controller } from "@hotwired/stimulus";
import axios from "axios";
import { enter, leave } from "el-transition";

export default class extends Controller {
  static targets = ["numberOfLikes", "heart", "modalButton", "modal"];
  static values = {
    projectId: Number,
    count: Number,
    liked: Boolean,
    toggleUrl: String,
  };

  connect() {
    this.render();
  }

  modify() {
    const previousLikeCount = this.countValue;
    const nextLiked = !this.likedValue;
    const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;

    this.setPending(true);
    axios({
      method: "post",
      url: this.toggleUrlValue,
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken,
      },
      data: {
        like: nextLiked,
      },
    })
      .then((response) => {
        this.likedValue = response.data.like;
        this.countValue = response.data.like_count;
        this.render();
        this.trackChange(this.likedValue, previousLikeCount);
      })
      .catch(() => {
        this.showError();
      })
      .finally(() => {
        this.setPending(false);
      });
  }

  render() {
    this.numberOfLikesTarget.textContent = this.countValue;
    this.heartTarget.className = this.likedValue ? "text-red-600 las la-heart block" : "lar la-heart block";
  }

  setPending(isPending) {
    const button = this.element.querySelector("button");
    if (!button) {
      return;
    }

    button.disabled = isPending;
    button.classList.toggle("opacity-60", isPending);
  }

  showError() {
    const button = this.element.querySelector("button");
    if (!button) {
      return;
    }

    button.classList.add("border-red-600", "text-red-600");
    button.setAttribute("aria-invalid", "true");
    button.title = "Could not update like";
    window.setTimeout(() => {
      button.classList.remove("border-red-600", "text-red-600");
      button.removeAttribute("aria-invalid");
      button.removeAttribute("title");
    }, 3000);
  }

  trackChange(likeValue, previousLikeCount) {
    if (!window.bwdTrack) {
      return;
    }

    window.bwdTrack("project like changed", {
      project_id: this.projectIdValue,
      like_value: likeValue,
      previous_like_count: previousLikeCount,
      new_like_count: this.countValue,
    });
  }

  toggleModal() {
    if (this.modalTarget.classList.contains("hidden")) {
      enter(this.modalTarget);
      if (window.bwdTrack) {
        window.bwdTrack("project like auth modal opened", {
          project_id: this.projectIdValue,
        });
      }
    } else {
      leave(this.modalTarget);
      if (window.bwdTrack) {
        window.bwdTrack("project like auth modal closed", {
          project_id: this.projectIdValue,
        });
      }
    }
  }
}
