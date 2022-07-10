import { Controller } from "@hotwired/stimulus";

export default class extends Controller {

  initialize() {
    console.log("Connected");
  }

  greet() {
    console.log("hello");
  }
}
