module.exports = {
    testEnvironment: "", 
    roots: ["<rootDir>/js-tests"],
    setupFilesAfterEnv: ["<rootDir>/js-tests/setup.js"],
    collectCoverage: true,    
    coverageDirectory: "jest_coverage", 
    coverageReporters: ["text", "lcov"], 
    moduleFileExtensions: ["js", "jsx", "json", "node"],
    moduleNameMapper: {
      "^cesium$": "<rootDir>/js-tests/__mocks__/cesium.js",
    },
    transformIgnorePatterns: ["/node_modules/"],
  };