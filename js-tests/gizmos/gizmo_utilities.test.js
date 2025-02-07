import $ from "jquery";

require("../../tethys_gizmos/static/tethys_gizmos/js/gizmo_utilities");

describe("gizmo_utilities.js", () => {
    let testElement;

    beforeEach(() => {
        // Set up a mock DOM element for testing
        document.body.innerHTML = `<div id="test-element" style="width: 100px; height: 100px;"></div>`;
        testElement = $("#test-element");
    });

    afterEach(() => {
        clearInterval(testElement[0].sizeTO);
    });

    test("should define $.fn.changeSize", () => {
        expect($.fn.changeSize).toBeDefined();
    });

    test("should call the callback function ", (done) => {
        const callback = jest.fn();

        testElement.changeSize(callback);

        setTimeout(() => {
            testElement.width(200);
            testElement.height(200);
        }, 50);

        setTimeout(() => {
            expect(callback).toHaveBeenCalledWith(testElement);
            done();
        }, 200);
    });

    test("should not trigger callback if size remains the same", (done) => {
        const callback = jest.fn();

        testElement.changeSize(callback);

        setTimeout(() => {
            expect(callback).not.toHaveBeenCalled();
            done();
        }, 200);
    });

    
});