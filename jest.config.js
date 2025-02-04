module.exports = {
    testEnvironment: "node", 
    roots: ["js-tests"],
    collectCoverage: true,    
    coverageDirectory: "jest_coverage", 
    coverageReporters: ["text", "lcov"], 
    moduleFileExtensions: ["js", "jsx", "json", "node"],
  };