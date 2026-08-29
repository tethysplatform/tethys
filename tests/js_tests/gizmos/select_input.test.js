import { execSync } from "child_process";
import path from "path";
import fs from "fs";

const { screen } = require("@testing-library/dom");
import userEvent from "@testing-library/user-event";

import TETHYS_SELECT_INPUT from "../../../tethys_gizmos/static/tethys_gizmos/js/select_input.js";

import $ from "jquery";
global.$ = $;
global.jQuery = $;

$.fn.select2 = jest.fn().mockImplementation(function () {
    return this;
});

let renderedHtml = "";

beforeAll(() => {
    const templateName = "tethys_gizmos/gizmos/select_input.html";
    const context = JSON.stringify({
        title: "Testing the select input gizmo",
        id: "test_select_input_id",
        options: [
            ["Option 1", "option1"],
            ["Option 2", "option2"],
            ["Option 3", "option3"],
        ],
        initial: "option2",
        display_text: "Choose an Option",
        name: "test_selector"
    });

    execSync(`python render_template.py ${templateName} '${context}'`, { stdio: "inherit" });
    const outputPath = path.resolve("./rendered_templates/test_select_input_output.html");
    renderedHtml = fs.readFileSync(outputPath, "utf8");
})

beforeEach(() => {
    document.body.innerHTML = renderedHtml;
    TETHYS_SELECT_INPUT.initSelectInput(".tethys-select2");
});

test("Gizmo renders correctly", () => {
    expect(screen.getByText("Option 1")).toBeInTheDocument();
    expect(screen.getByText("Option 2")).toBeInTheDocument();
    expect(screen.getByText("Option 3")).toBeInTheDocument();
});

test("The initially selected value is visible to the user", () => {
    const select = screen.getByLabelText("Choose an Option");
    expect(select).toHaveDisplayValue("Option 2");
});


test("User can select a different option", async () => {
    const user = userEvent.setup();
    const select = screen.getByLabelText("Choose an Option");

    await user.selectOptions(select, "option3");

    expect(select).toHaveDisplayValue("Option 3");
});