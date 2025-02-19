import $ from "jquery";
import * as Cesium from "cesium";

global.Cesium = Cesium;

const CESIUM_MAP_VIEW = require("../../../tethys_gizmos/static/tethys_gizmos/js/cesium_map_view");
const { _testOnly } = CESIUM_MAP_VIEW; 

jest.mock('cesium');

jest.mock("jquery" , () => {
  return jest.fn(() => ({
    data: jest.fn((key) => {
      const mockData = {
        "cesium-ion-token": "mock_token",
        clock: {
            clock: {
                currentTime: "2025-02-10T12:15:00Z",
                startTime: "2025-02-10T12:00:00Z",
                stopTime: "2025-02-10T12:30:00Z",
            },
        },
        options: { shouldInitialize: true },
      };
      return mockData[key];
    }),
  }));
});

beforeEach(() => {
    jest.clearAllMocks();
    document.body.innerHTML = `
        <div id="cesium_map_view"></div>
        <textarea id="cesium_map_view_geometry"></textarea>
        <div id="cesium_map_view_loggin"></div>
    `;
})

describe("CESIUM_MAP_VIEW", () => {
    test("should initialize the map correctly", () => {
        expect(CESIUM_MAP_VIEW).toBeDefined(); 
        expect(typeof CESIUM_MAP_VIEW.getMap).toBe("function"); 
        expect(typeof CESIUM_MAP_VIEW.reInitializeMap).toBe("function"); 
    });
});

describe("is_empty_or_undefined", () => {
    test("should return true for undefined values", () => {
        expect(_testOnly.is_empty_or_undefined(undefined)).toBe(true);
    });

    test("should return true for empty values", () => {
        expect(_testOnly.is_empty_or_undefined("")).toBe(true);
        expect(_testOnly.is_empty_or_undefined(null)).toBe(true);
    });

    test("should return true for non-empty values", () => {
        expect(_testOnly.is_empty_or_undefined("test")).toBe(true);
        expect(_testOnly.is_empty_or_undefined(0)).toBe(true);
    });

    test("should return true for an empty object", () => {
        expect(_testOnly.is_empty_or_undefined({})).toBe(true);
    });

    test("should return false for non-empty object", () => {
        expect(_testOnly.is_empty_or_undefined({ key: "value" })).toBe(false);
    });
})

describe("need_to_run", () => {
    test("should return true if object contains a Cesium reference", () => {
        const obj = {
            someProperty: {
                "Cesium.Cartesian3": [0, 0, 0],  // This should trigger `true`
            }
        };
        expect(_testOnly.need_to_run(obj)).toBe(true);
    });

    test("should return true for nested Cesium references", () => {
        const obj = {
            level1: {
                level2: {
                    level3: {
                        "Cesium.Color": "RED"
                    }
                }
            }
        };
        expect(_testOnly.need_to_run(obj)).toBe(true);
    });

    test("should return false for objects without Cesium references", () => {
        const obj = {
            level1: {
                level2: {
                    level3: {
                        someKey: "someValue",
                    }
                }
            }
        };
        expect(_testOnly.need_to_run(obj)).toBe(false);
    });

    test("should return false for an empty object", () => {
        expect(_testOnly.need_to_run({})).toBe(false);
    });

    test("should return false for non-object values", () => {
        expect(_testOnly.need_to_run(null)).toBe(false);
        expect(_testOnly.need_to_run(undefined)).toBe(false);
        expect(_testOnly.need_to_run("string")).toBe(false);
        expect(_testOnly.need_to_run(123)).toBe(false);
        expect(_testOnly.need_to_run([])).toBe(false);
    });

    test("should return false when object has properties but no Cesium references", () => {
        const obj = {
            someKey: {
                anotherKey: {
                    deeperKey: "notCesium"
                }
            }
        };
        expect(_testOnly.need_to_run(obj)).toBe(false);
    });

    test("should return true when Cesium reference appears deeper in the object", () => {
        const obj = {
            someKey: {
                anotherKey: {
                    deeperKey: {
                        "Cesium.SceneMode": "MORPHING"
                    }
                }
            }
        };
        expect(_testOnly.need_to_run(obj)).toBe(true);
    });
});
