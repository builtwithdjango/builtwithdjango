import "../styles/tailwind.css";

import "@hotwired/turbo";

import { Application } from "@hotwired/stimulus";
import { definitionsFromContext } from "@hotwired/stimulus-webpack-helpers";

// Turbo
window.document.addEventListener("DOMContentLoaded", function () {
  window.console.log("dom ready 1");
});

document.addEventListener('turbo:load', function () {
  console.log('turbo:load');
});

document.addEventListener("turbo:before-cache", function () {
  console.log('turbo:before-cache');
  const form = document.querySelector('form');
  if (form) {
    form.reset();
  }
});

// Stimulus
const application = Application.start();
const context = require.context("../controllers", true, /\.js$/);
application.load(definitionsFromContext(context));
