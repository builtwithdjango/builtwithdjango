import "../styles/tailwind.css";

import { Application } from "@hotwired/stimulus";
import { definitionsFromContext } from "@hotwired/stimulus-webpack-helpers";
import Dropdown from 'stimulus-dropdown';
import Reveal from 'stimulus-reveal-controller';


// Stimulus
const application = Application.start();
const context = require.context("../controllers", true, /\.js$/);
application.load(definitionsFromContext(context));

application.register('dropdown', Dropdown);
application.register('reveal', Reveal);
