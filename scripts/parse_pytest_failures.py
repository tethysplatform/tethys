#!/usr/bin/env python3
"""
Parse pytest output and categorize test failures into different issue types.
"""

import re
from typing import Dict, List, Any


class PytestOutputParser:
    def __init__(self, pytest_output_file: str):
        self.pytest_output_file = pytest_output_file
        self.issues = {
            "database_access_issues": [],
            "model_does_not_exist_issues": [],
            "missing_module_issues": [],
            "url_routing_issues": [],
        }

        # Regex patterns for different error types
        self.patterns = {
            "database_access": re.compile(
                r'RuntimeError: Database access not allowed, use the "django_db" mark'
            ),
            "model_does_not_exist": re.compile(
                r"(\w+\.)*(\w+)\.DoesNotExist: .+ matching query does not exist"
            ),
            "missing_module": re.compile(
                r"ModuleNotFoundError: No module named \'([^\']+)\'"
            ),
            "url_routing": re.compile(
                r"django\.urls\.exceptions\.NoReverseMatch: \'([^\']+)\' is not a registered namespace"
            ),
        }

        # Pattern to match failed test identifiers
        self.failed_test_pattern = re.compile(r"FAILED\s+([^:]+)::([^:]+)::([^\s]+)")

    def parse_output(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Parse the pytest output file and categorize failures.

        Returns:
            Dictionary with categorized test failures
        """
        try:
            with open(self.pytest_output_file, "r") as f:
                content = f.read()
        except FileNotFoundError:
            print(
                f"Error: Could not find pytest output file: {self.pytest_output_file}"
            )
            return self.issues
        except Exception as e:
            print(f"Error reading file {self.pytest_output_file}: {e}")
            return self.issues

        # Split content into sections
        lines = content.split("\n")

        # First, find all failed tests from the short summary
        failed_tests = self._extract_failed_tests(lines)

        # Then categorize each failure by finding its detailed error message
        self._categorize_failures(content, failed_tests)

        return self.issues

    def _extract_failed_tests(self, lines: List[str]) -> List[Dict[str, str]]:
        """Extract all failed test identifiers from the short summary section."""
        failed_tests = []
        in_summary = False

        for line in lines:
            if "short test summary info" in line:
                in_summary = True
                continue
            elif in_summary and line.startswith("="):
                break
            elif in_summary and line.startswith("FAILED"):
                match = self.failed_test_pattern.search(line)
                if match:
                    file_path, class_name, method_name = match.groups()
                    failed_tests.append(
                        {
                            "file_path": file_path,
                            "class_name": class_name,
                            "method_name": method_name,
                            "full_identifier": f"{file_path}::{class_name}::{method_name}",
                        }
                    )

        return failed_tests

    def _categorize_failures(self, content: str, failed_tests: List[Dict[str, str]]):
        """Categorize each failed test by finding its error message in the detailed output."""

        # Split content by test failure sections
        failure_sections = content.split(
            "_" * 20
        )  # Failure sections start with underscores

        for test in failed_tests:
            error_type = self._find_error_type_for_test(failure_sections, test)

            if error_type:
                category = self._get_category_for_error_type(error_type)
                if category:
                    test_info = {
                        "file_path": test["file_path"],
                        "class_name": test["class_name"],
                        "method_name": test["method_name"],
                        "full_identifier": test["full_identifier"],
                        "error_type": error_type["type"],
                        "error_message": error_type["message"],
                    }

                    # Add additional context based on error type
                    if error_type["type"] == "missing_module":
                        test_info["missing_module"] = error_type.get("module_name", "")
                    elif error_type["type"] == "url_routing":
                        test_info["namespace"] = error_type.get("namespace", "")
                    elif error_type["type"] == "model_does_not_exist":
                        test_info["model_name"] = error_type.get("model_name", "")

                    self.issues[category].append(test_info)

    def _find_error_type_for_test(
        self, failure_sections: List[str], test: Dict[str, str]
    ) -> Dict[str, str]:
        """Find the error type for a specific test by searching through failure sections."""

        # Look for a section that contains this test
        test_identifier_parts = [
            test["class_name"],
            test["method_name"],
            test["file_path"].split("/")[-1],  # Just the filename
        ]

        for section in failure_sections:
            # Check if this section is about our test
            if any(part in section for part in test_identifier_parts):
                # Try to match each error pattern
                for error_type, pattern in self.patterns.items():
                    match = pattern.search(section)
                    if match:
                        error_info = {"type": error_type, "message": match.group(0)}

                        # Extract additional info based on error type
                        if error_type == "missing_module":
                            error_info["module_name"] = match.group(1)
                        elif error_type == "url_routing":
                            error_info["namespace"] = match.group(1)
                        elif error_type == "model_does_not_exist":
                            # Extract model name from the full match
                            model_match = re.search(
                                r"(\w+)\.DoesNotExist:", match.group(0)
                            )
                            if model_match:
                                error_info["model_name"] = model_match.group(1)

                        return error_info

        # If no specific pattern matches, try to categorize based on generic error patterns
        return self._fallback_error_detection(failure_sections, test)

    def _fallback_error_detection(
        self, failure_sections: List[str], test: Dict[str, str]
    ) -> Dict[str, str]:
        """Fallback method to detect error types using broader patterns."""

        test_identifier_parts = [test["class_name"], test["method_name"]]

        for section in failure_sections:
            if any(part in section for part in test_identifier_parts):
                # Check for common error patterns
                if "DoesNotExist:" in section:
                    return {
                        "type": "model_does_not_exist",
                        "message": "Model DoesNotExist error",
                        "model_name": "Unknown",
                    }
                elif "ModuleNotFoundError" in section:
                    return {
                        "type": "missing_module",
                        "message": "Module not found error",
                        "module_name": "Unknown",
                    }
                elif "NoReverseMatch" in section:
                    return {
                        "type": "url_routing",
                        "message": "URL routing error",
                        "namespace": "Unknown",
                    }
                elif "Database access not allowed" in section:
                    return {
                        "type": "database_access",
                        "message": "Database access not allowed",
                    }

        return None

    def _get_category_for_error_type(self, error_type: Dict[str, str]) -> str:
        """Map error types to category names."""
        mapping = {
            "database_access": "database_access_issues",
            "model_does_not_exist": "model_does_not_exist_issues",
            "missing_module": "missing_module_issues",
            "url_routing": "url_routing_issues",
        }
        return mapping.get(error_type["type"])

    def print_summary(self):
        """Print a summary of categorized issues."""
        print("=" * 80)
        print("PYTEST FAILURE CATEGORIZATION SUMMARY")
        print("=" * 80)

        total_issues = sum(len(issues) for issues in self.issues.values())
        print(f"Total categorized issues: {total_issues}")
        print()

        for category, issues in self.issues.items():
            if issues:
                print(f"{category.replace('_', ' ').title()}: {len(issues)} issues")
                print("-" * 40)
                for issue in issues[:5]:  # Show first 5 of each type
                    print(
                        f"  • {issue['file_path']}::{issue['class_name']}::{issue['method_name']}"
                    )
                    if len(issue["error_message"]) < 100:
                        print(f"    {issue['error_message']}")
                    else:
                        print(f"    {issue['error_message'][:97]}...")

                if len(issues) > 5:
                    print(f"  ... and {len(issues) - 5} more")
                print()

    def save_to_file(self, output_file: str = "categorized_test_failures.py"):
        """Save the categorized issues to a Python file."""

        with open(output_file, "w") as f:
            f.write("#!/usr/bin/env python3\n")
            f.write('"""\n')
            f.write("Categorized pytest test failures\n")
            f.write(f"Generated from: {self.pytest_output_file}\n")
            f.write('"""\n\n')

            f.write("categorized_test_failures = {\n")

            for category, issues in self.issues.items():
                f.write(f'    "{category}": [\n')
                for issue in issues:
                    f.write("        {\n")
                    for key, value in issue.items():
                        if isinstance(value, str):
                            # Escape quotes and other special characters
                            escaped_value = value.replace("\\", "\\\\").replace(
                                '"', '\\"'
                            )
                            f.write(f'            "{key}": "{escaped_value}",\n')
                        else:
                            f.write(f'            "{key}": {value},\n')
                    f.write("        },\n")
                f.write("    ],\n")

            f.write("}\n\n")

            # Add summary statistics
            f.write("# Summary Statistics\n")
            f.write("summary = {\n")
            for category, issues in self.issues.items():
                f.write(f'    "{category}": {len(issues)},\n')
            f.write("}\n")

            total = sum(len(issues) for issues in self.issues.values())
            f.write(f"\n# Total issues: {total}\n")

        print(f"Categorized issues saved to: {output_file}")


def main():
    parser = PytestOutputParser("pytest_output.txt")
    issues = parser.parse_output()

    # Print summary
    parser.print_summary()

    # Save to file
    parser.save_to_file()

    return issues


if __name__ == "__main__":
    main()
