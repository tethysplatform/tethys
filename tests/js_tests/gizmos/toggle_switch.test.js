import $ from "jquery";

// Mock Bootstrap Switch plugin
$.fn.bootstrapSwitch = jest.fn();

// Import the module
const TETHYS_TOGGLE_SWITCH = require("../../../tethys_gizmos/static/tethys_gizmos/js/toggle_switch");

describe("TETHYS_TOGGLE_SWITCH", () => {
    beforeEach(() => {
        jest.clearAllMocks(); // Reset mocks before each test

        // Set up a mock DOM element for testing
        document.body.innerHTML = `
            <input type="checkbox" class="bootstrap-switch">
        `;
    });

    test("Module should have initToggleSwitch function", () => {
        expect(TETHYS_TOGGLE_SWITCH).toHaveProperty("initToggleSwitch");
        expect(typeof TETHYS_TOGGLE_SWITCH.initToggleSwitch).toBe("function");
    });

    test("initToggleSwitch should initialize Bootstrap Switch", () => {
        const switchElement = $(".bootstrap-switch");

        TETHYS_TOGGLE_SWITCH.initToggleSwitch(switchElement);

        expect($.fn.bootstrapSwitch).toHaveBeenCalledTimes(1);
    });

    test("Automatically initializes switch elements on page load", (done) => {
        // Ensure that the bootstrapSwitch function was called during module initialization
        const switchSpy = jest.spyOn($.fn, "bootstrapSwitch");

        // Wait for jQuery's document ready function
        setTimeout(() => {
            // Ensure bootstrapSwitch was called
            expect(switchSpy).toHaveBeenCalled();
            switchSpy.mockRestore();
            done();
        }, 100);
    });
});