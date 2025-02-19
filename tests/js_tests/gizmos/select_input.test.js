import $ from "jquery";

$.fn.select2 = jest.fn();

const TETHYS_SELECT_INPUT = require("../../../tethys_gizmos/static/tethys_gizmos/js/select_input");

describe("TETHYS_SELECT_INPUT", () => {
    beforeEach(() => {
        // Set up a mock DOM element for testing
        document.body.innerHTML = `
            <select class="tethys-select2" data-select2-options='{"placeholder": "Select an option"}'>
            <option value="1">Option 1</option>
            <option value="2">Option 2</option>
            </select>
        `;
  });

  test("should initialize Select2 on document ready", (done) => {
    const select2Spy = jest.spyOn($.fn, "select2");

    // Wait for jQuery's document ready function
    setTimeout(() => {
        // Ensure select2 was called
        expect(select2Spy).toHaveBeenCalled();
        select2Spy.mockRestore();
        done();
    }, 100);
  })

  test("Module should have initSelectInput function", () => {
      expect(TETHYS_SELECT_INPUT).toHaveProperty("initSelectInput");
      expect(typeof TETHYS_SELECT_INPUT.initSelectInput).toBe("function");
  });

  test("initSelectInput should initialize Select2 on elements", () => {
      const selectElement = $(".tethys-select2");

      TETHYS_SELECT_INPUT.initSelectInput(selectElement);

      expect($.fn.select2).toHaveBeenCalledTimes(1);
  });

  test("jQuery should call select2 with correct options", () => {
    const selectElement = $(".tethys-select2");

    // Mock jQuery's .data() method to return select2 options
    $.fn.data = jest.fn(() => ({ placeholder: "Select an option" }));

    TETHYS_SELECT_INPUT.initSelectInput(selectElement);

    expect($.fn.select2).toHaveBeenCalledWith({ placeholder: "Select an option" });
  });

  test("Automatically initializes on page load", () => {
      // Ensure that the select2 function was called during module initialization
      expect($.fn.select2).toHaveBeenCalled();
  });

});
  
    
    