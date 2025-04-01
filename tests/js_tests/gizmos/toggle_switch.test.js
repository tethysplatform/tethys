import { execSync } from "child_process";
import fs from "fs";
import path from "path";
const { screen, fireEvent } = require("@testing-library/dom");

import TOGGLE_SWITCH from "../../../tethys_gizmos/static/tethys_gizmos/js/toggle_switch.js"

window.TOGGLE_SWITCH = TOGGLE_SWITCH;

import $ from "jquery";
global.$ = $;
global.jQuery = $;
$.fn.bootstrapSwitch = jest.fn();

let renderedHtml = '';

beforeAll(() => {
    // Render the template using Python script with a provided context
    const templateName = "tethys_gizmos/gizmos/toggle_switch.html";
    const context = JSON.stringify({
        name: "test_toggle_switch",
        display_text: "Test Toggle Switch",
        on_label: "On Label Text",
        off_label: "Off Label Text",
        initial: false
    });
    execSync(`python render_template.py ${templateName} '${context}' `, { stdio: "inherit" });
    // Read the rendered HTML file
    const outputPath = path.resolve("./rendered_templates/test_toggle_switch_output.html");
    renderedHtml = fs.readFileSync(outputPath, "utf8");
});

beforeEach(() => {
    // Set up the document body with the rendered HTML before each test runs
    document.body.innerHTML = renderedHtml;

    // Initialize the toggle switch
    TOGGLE_SWITCH.initToggleSwitch(".bootstrap-switch");
});

test("Gizmo renders correctly", () => {
    const toggleSwitch = screen.getByLabelText("Test Toggle Switch");
    expect(toggleSwitch).toBeInTheDocument();
});

test("Toggle switch is unchecked by default", () => {
    const toggleInput = screen.getByLabelText("Test Toggle Switch");
    expect(toggleInput).not.toBeChecked();
});

test("Toggle switch initialization calls bootstrapSwitch", () => {
    expect($.fn.bootstrapSwitch).toHaveBeenCalled();
});

test("User can toggle the switch", () => {
    const toggleInput = screen.getByLabelText("Test Toggle Switch");

    // Check if the toggle switch is initially unchecked
    expect(toggleInput).not.toBeChecked();
  
    // Simulate click
    fireEvent.click(toggleInput);
    expect(toggleInput).toBeChecked();
  
    // Simulate click again
    fireEvent.click(toggleInput);
    expect(toggleInput).not.toBeChecked();
});