import $ from "jquery";

// Mock jQuery functions
$.fn.addClass = jest.fn();
$.fn.removeClass = jest.fn();

// Import the module AFTER mocking jQuery
const SLIDE_SHEET = require("../../../tethys_gizmos/static/tethys_gizmos/js/slide_sheet");

describe("SLIDE_SHEET", () => {
    beforeEach(() => {
        jest.clearAllMocks(); // Reset mocks before each test

        // Set up a mock DOM element for testing
        document.body.innerHTML = `
            <div id="test-slide" class="slide-sheet"></div>
        `;
    });

    test("Module should have open and close functions", () => {
        expect(SLIDE_SHEET).toHaveProperty("open");
        expect(typeof SLIDE_SHEET.open).toBe("function");

        expect(SLIDE_SHEET).toHaveProperty("close");
        expect(typeof SLIDE_SHEET.close).toBe("function");
    });

    test("open should add 'show' class to slide-sheet", () => {
        SLIDE_SHEET.open("test-slide");

        expect($("#test-slide.slide-sheet").addClass).toHaveBeenCalledWith("show");
    });

    test("close should remove 'show' class from slide-sheet", () => {
        SLIDE_SHEET.close("test-slide");

        expect($("#test-slide.slide-sheet").removeClass).toHaveBeenCalledWith("show");
    });

    test("open does nothing if id is empty", () => {
        SLIDE_SHEET.open("");

        expect($.fn.addClass).not.toHaveBeenCalled();
    });

    test("close does nothing if id is empty", () => {
        SLIDE_SHEET.close("");

        expect($.fn.removeClass).not.toHaveBeenCalled();
    });
});