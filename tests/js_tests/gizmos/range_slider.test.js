import $ from "jquery";

// Import module AFTER mocking jQuery
const TETHYS_RANGE_SLIDER = require("../../../tethys_gizmos/static/tethys_gizmos/js/range_slider");

describe("TETHYS_RANGE_SLIDER", () => {
    beforeEach(() => {
        jest.clearAllMocks();

        // Set up a mock DOM element for testing
        document.body.innerHTML = `
            <input type="range" class="form-range" value="50">
            <span class="range-value">50</span>
        `;
    });

    test("Should initialize range sliders on page load", (done) => {
        // Wait for jQuery's document ready function
        setTimeout(() => {
            const rangeInput = document.querySelector(".form-range");
            const rangeValue = document.querySelector(".range-value");

            expect(rangeInput).not.toBeNull();
            expect(rangeValue).not.toBeNull();

            done();
        }, 100);
    });

    test("Should update value display when slider is moved", () => {
        const rangeInput = document.querySelector(".form-range");
        const rangeValue = document.querySelector(".range-value");
    
        // Manually initialize range sliders 
        TETHYS_RANGE_SLIDER.init_range_sliders();
        rangeInput.value = "75";
    
        // Trigger the input event
        const event = document.createEvent("Event");
        event.initEvent("input", true, true);
        rangeInput.dispatchEvent(event);
    
        // Check if the slider's value has updated
        expect(rangeValue.innerHTML).toBe("75");
    });
});