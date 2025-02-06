module.exports = {
    testEnvironment: "node", 
    roots: ["<rootDir>/js-tests"],
    setupFilesAfterEnv: ["<rootDir>/js-tests/setup.js"],
    collectCoverage: true,    
    coverageDirectory: "jest_coverage", 
    coverageReporters: ["text", "lcov"], 
    moduleFileExtensions: ["js", "jsx", "json", "node"],
  };