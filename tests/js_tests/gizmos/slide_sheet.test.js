import { execSync } from "child_process";
import fs from "fs";
import path from "path";
const { screen, fireEvent, waitFor } = require("@testing-library/dom");

import SLIDE_SHEET from "../../../tethys_gizmos/static/tethys_gizmos/js/slide_sheet.js"

window.SLIDE_SHEET = SLIDE_SHEET;

let renderedHtml = '';

const SLIDE_SHEET_ID = "test_slide_sheet_id"

function simulateShowClassStyling() {
    // Simulate the CSS class 'show' to display or hide the slide sheet
    // To be used in the tests any time a slide sheet is opened or closed 
    // manually or with a simulated button press
    document.querySelectorAll('.slide-sheet').forEach((element) => {
        if (element.classList.contains('show')) {
            element.style.display = 'block';
        }
        else {
            element.style.display = 'none';
        }
    });
}

beforeAll(() => {
    // Render the template using Python script with a provided context
    const templateName = "tethys_gizmos/gizmos/slide_sheet.html";
    const context = JSON.stringify({
        title: "Testing the slide sheet gizmo",
        id: SLIDE_SHEET_ID,
        content_template: "test_template.html"
    });
    execSync(`python render_template.py ${templateName} '${context}' `, { stdio: "inherit" });
    // Read the rendered HTML file
    const outputPath = path.resolve("./rendered_templates/test_slide_sheet_output.html");
    renderedHtml = fs.readFileSync(outputPath, "utf8");
})

beforeEach(() => {
    // Set up the document body with the rendered HTML before each test runs
    document.body.innerHTML = renderedHtml;
});

test("Gizmo renders correctly", () => {
    const sheet = document.getElementById(SLIDE_SHEET_ID);
    expect(sheet).toBeInTheDocument();
    expect(sheet).toHaveClass("slide-sheet");
});

test("Clicking the open button should show the slide sheet", async () => {
    const sheet = document.getElementById(SLIDE_SHEET_ID);
    // Make sure the sheet is not visible to start off
    expect(sheet).not.toBeVisible();
    // Add a button to open the slide sheet
    const button = document.createElement("button");
    button.className = "btn-open";
    button.textContent = "Open Slide Sheet";
    document.body.appendChild(button);
    // Add an event listener to the button to open the slide sheet
    const openButton = screen.getByText("Open Slide Sheet");
    openButton.addEventListener("click", () => {
        SLIDE_SHEET.open(SLIDE_SHEET_ID);
    });
    fireEvent.click(openButton);
    simulateShowClassStyling();
    // Check that the slide sheet is now visible
    expect(sheet).toBeVisible();
});


test("Clicking the close button should hide the slide sheet", async () => {
    // Open the slide sheet first
    SLIDE_SHEET.open(SLIDE_SHEET_ID);
    simulateShowClassStyling();
    const sheet = document.getElementById(SLIDE_SHEET_ID);
    // Make sure the sheet is visible to start off
    expect(sheet).toBeVisible();
    // Now close it
    const closeButton = document.querySelector(".btn-close");
    fireEvent.click(closeButton); 
    simulateShowClassStyling();
    // Check that the sheet is no longer visible
    expect(sheet).not.toBeVisible();
});