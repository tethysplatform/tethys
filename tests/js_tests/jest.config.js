module.exports = {
    testEnvironment: "jsdom", 
    roots: ["<rootDir>"],
    setupFiles: ["<rootDir>/jest.polyfills.js"],
    setupFilesAfterEnv: ["<rootDir>/setup.js"],
    collectCoverage: true,    
    coverageDirectory: "jest_coverage", 
    coverageReporters: ["text", "lcov"], 
    moduleFileExtensions: ["js", "jsx", "json", "node"],
    moduleNameMapper: {
      "^cesium$": "<rootDir>/__mocks__/cesium.js",
    },
    transformIgnorePatterns: ["/node_modules/"],
  };