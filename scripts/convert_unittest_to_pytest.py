#!/usr/bin/env python3
"""
Convert unittest-style test files to pytest-style test files.

This script converts class-based unittest tests to function-based pytest tests:
- Removes TestCase classes and converts methods to functions
- Transforms setUp/tearDown to pytest fixtures with yield
- Converts all self.assert* to plain assert statements
- Converts helper methods to pytest fixtures
- Properly dedents function bodies
- Preserves decorators like @mock.patch
"""

import re
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Optional, Dict


class TestConverter:
    """Converts unittest test classes to pytest functions."""

    # Mapping of unittest assertions to pytest equivalents
    ASSERTION_MAP = {
        # assertEqual with detailed handling for parentheses
        r"self\.assertEqual\(": "assert ",
        r"self\.assertNotEqual\(": "assert ",
        r"self\.assertTrue\((.*?)\)": r"assert \1",
        r"self\.assertFalse\((.*?)\)": r"assert not \1",
        r"self\.assertIs\((.*?),\s*(.*?)\)": r"assert \1 is \2",
        r"self\.assertIsNot\((.*?),\s*(.*?)\)": r"assert \1 is not \2",
        r"self\.assertIsNone\((.*?)\)": r"assert \1 is None",
        r"self\.assertIsNotNone\((.*?)\)": r"assert \1 is not None",
        r"self\.assertIn\((.*?),\s*(.*?)\)": r"assert \1 in \2",
        r"self\.assertNotIn\((.*?),\s*(.*?)\)": r"assert \1 not in \2",
        r"self\.assertIsInstance\((.*?),\s*(.*?)\)": r"assert isinstance(\1, \2)",
        r"self\.assertNotIsInstance\((.*?),\s*(.*?)\)": r"assert not isinstance(\1, \2)",
        r"self\.assertGreater\((.*?),\s*(.*?)\)": r"assert \1 > \2",
        r"self\.assertGreaterEqual\((.*?),\s*(.*?)\)": r"assert \1 >= \2",
        r"self\.assertLess\((.*?),\s*(.*?)\)": r"assert \1 < \2",
        r"self\.assertLessEqual\((.*?),\s*(.*?)\)": r"assert \1 <= \2",
    }

    def __init__(self, content: str):
        self.content = content
        self.lines = content.split("\n")
        self.has_pytest_import = "import pytest" in content

    def convert(self) -> str:
        """Convert the entire file."""
        # Process imports
        self.content = self._process_imports()

        # Process test classes
        self.content = self._process_test_classes()

        return self.content

    def _process_imports(self) -> str:
        """Update imports for pytest."""
        lines = self.content.split("\n")
        new_lines = []

        for line in lines:
            # Remove standalone unittest import (but keep unittest.mock)
            if re.match(r"^import unittest\s*$", line):
                continue
            # Remove TestCase from unittest imports
            elif re.match(r"^from unittest import.*TestCase", line):
                # Keep other imports from unittest
                parts = line.split("import")[1].strip().split(",")
                remaining = [p.strip() for p in parts if "TestCase" not in p]
                if remaining:
                    new_lines.append(f"from unittest import {', '.join(remaining)}")
                continue

            new_lines.append(line)

        # Ensure pytest is imported
        if not self.has_pytest_import:
            # Find the right place to insert (after other imports)
            insert_idx = 0
            for i, line in enumerate(new_lines):
                if line.startswith("import ") or line.startswith("from "):
                    insert_idx = i + 1

            # Check if pytest import already exists
            has_pytest = any(
                "import pytest" in line for line in new_lines[: insert_idx + 5]
            )
            if not has_pytest:
                new_lines.insert(insert_idx, "import pytest")

        return "\n".join(new_lines)

    def _process_test_classes(self) -> str:
        """Convert test classes to functions."""
        lines = self.content.split("\n")
        new_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # Check if this is a test class
            class_match = re.match(r"^class\s+(\w+)\s*\((.*?TestCase.*?)\):", line)
            if class_match:
                class_name = class_match.group(1)
                # Process the entire class
                class_lines, i = self._extract_class(lines, i)
                converted = self._convert_test_class(class_lines, class_name)
                new_lines.extend(converted)
            else:
                new_lines.append(line)
                i += 1

        return "\n".join(new_lines)

    def _extract_class(self, lines: List[str], start_idx: int) -> Tuple[List[str], int]:
        """Extract all lines belonging to a class."""
        class_lines = [lines[start_idx]]
        i = start_idx + 1

        # Find the indentation of the class
        class_indent = len(lines[start_idx]) - len(lines[start_idx].lstrip())

        # Collect all lines until we hit something at the same or lower indentation
        while i < len(lines):
            line = lines[i]
            if line.strip() == "":
                class_lines.append(line)
                i += 1
                continue

            current_indent = len(line) - len(line.lstrip())
            if current_indent <= class_indent and line.strip():
                # We've hit the end of the class
                break

            class_lines.append(line)
            i += 1

        return class_lines, i

    def _convert_test_class(self, class_lines: List[str], class_name: str) -> List[str]:
        """Convert a test class to pytest functions."""
        result = []

        # Find class indentation
        class_indent = len(class_lines[0]) - len(class_lines[0].lstrip())

        # Extract setUp, tearDown, helper methods, and test methods
        setup_method = None
        teardown_method = None
        setupclass_method = None
        teardownclass_method = None
        helper_methods = []
        test_methods = []
        class_properties = set()  # Track cls.property references

        i = 1  # Skip class definition
        while i < len(class_lines):
            line = class_lines[i]

            # Check for method definition (could be multi-line)
            if re.match(r"^(\s*)def\s+(\w+)\s*\(", line):
                method_indent = len(line) - len(line.lstrip())
                method_name_match = re.match(r"^\s*def\s+(\w+)\s*\(", line)
                method_name = method_name_match.group(1)

                # Collect full method signature (might span multiple lines)
                # Start from the def line, not from decorator lines
                sig_lines = [line]
                j = i
                # Keep collecting lines until we find the closing "):"
                while "):" not in sig_lines[-1]:
                    j += 1
                    if j < len(class_lines):
                        sig_lines.append(class_lines[j])
                    else:
                        break

                # Extract parameters from full signature
                full_sig = " ".join(ln.strip() for ln in sig_lines)
                # Check for cls parameter (classmethod)
                if "cls" in full_sig:
                    params_match = re.search(
                        r"\(\s*cls\s*,?\s*(.*?)\s*\)\s*:", full_sig
                    )
                else:
                    params_match = re.search(
                        r"\(\s*self\s*,\s*(.*?)\s*\)\s*:", full_sig
                    )
                method_params = params_match.group(1) if params_match else ""

                # Extract the method (including decorators and body)
                method_lines, i = self._extract_method_with_decorators(
                    class_lines, i, method_indent
                )

                if method_name == "setUp":
                    setup_method = method_lines
                elif method_name == "tearDown":
                    teardown_method = method_lines
                elif method_name == "setUpClass":
                    setupclass_method = method_lines
                elif method_name == "tearDownClass":
                    teardownclass_method = method_lines
                elif method_name.startswith("test_"):
                    test_methods.append((method_name, method_params, method_lines))
                else:
                    # Helper method - convert to fixture
                    helper_methods.append((method_name, method_params, method_lines))
            else:
                i += 1

        # Generate module-scoped fixture for setUpClass/tearDownClass
        class_fixture_name = None
        if setupclass_method or teardownclass_method:
            class_fixture_name = "setup_class"
            class_fixture, class_props = self._generate_class_fixture(
                setupclass_method, teardownclass_method, class_indent
            )
            class_properties.update(class_props)
            result.extend(class_fixture)
            result.append("")
            result.append("")

        # Generate fixture for setUp/tearDown
        fixture_name = None
        instance_properties = set()
        if setup_method or teardown_method:
            fixture_name = "setup_test"
            fixture, instance_props = self._generate_setup_fixture(
                setup_method, teardown_method, class_indent
            )
            instance_properties.update(instance_props)
            result.extend(fixture)
            result.append("")
            result.append("")

        # Convert helper methods to fixtures
        helper_fixtures = {}
        for method_name, method_params, method_lines in helper_methods:
            fixture = self._convert_helper_to_fixture(
                method_name, method_params, method_lines, class_indent
            )
            result.extend(fixture)
            result.append("")
            result.append("")
            helper_fixtures[method_name] = f"{method_name}_fixture"

        # Convert each test method
        for method_name, method_params, method_lines in test_methods:
            converted = self._convert_test_method(
                method_name,
                method_params,
                method_lines,
                class_indent,
                fixture_name,
                helper_fixtures,
                class_fixture_name,
                class_properties,
                instance_properties,
            )
            result.extend(converted)
            result.append("")
            result.append("")

        # Remove trailing empty lines
        while result and result[-1] == "":
            result.pop()

        return result

    def _extract_method_with_decorators(
        self, lines: List[str], start_idx: int, method_indent: int
    ) -> Tuple[List[str], int]:
        """Extract all lines belonging to a method, including decorators above it."""
        # Look backwards to find where decorators start
        decorator_start_idx = start_idx
        j = start_idx - 1
        found_decorator = False

        while j >= 0:
            line = lines[j]
            stripped = line.strip()

            if not stripped:
                # Empty line - keep looking backward only if we haven't found decorators yet
                if found_decorator:
                    break
                j -= 1
                continue

            line_indent = len(line) - len(line.lstrip())

            # Check if this is a decorator at method level
            if stripped.startswith("@") and line_indent == method_indent:
                decorator_start_idx = j
                found_decorator = True
                j -= 1
            # Check if this is part of decorator region (continuation or decorator args)
            elif found_decorator and line_indent >= method_indent:
                # This is part of the decorator region (multi-line decorator or args)
                decorator_start_idx = j
                j -= 1
            else:
                # Hit something else - stop
                break

        # Now extract from decorator_start_idx through method body
        method_lines = []
        i = decorator_start_idx

        # Collect all lines from decorators through method signature
        while i <= start_idx:
            method_lines.append(lines[i])
            i += 1

        # Continue collecting signature lines if multi-line
        while i < len(lines) and "):" not in lines[i - 1]:
            method_lines.append(lines[i])
            i += 1

        # Now collect the method body
        while i < len(lines):
            line = lines[i]
            if line.strip() == "":
                method_lines.append(line)
                i += 1
                continue

            current_indent = len(line) - len(line.lstrip())
            if current_indent <= method_indent and line.strip():
                break

            method_lines.append(line)
            i += 1

        return method_lines, i

    def _extract_method(
        self, lines: List[str], start_idx: int, method_indent: int
    ) -> Tuple[List[str], int]:
        """Extract all lines belonging to a method."""
        method_lines = [lines[start_idx]]
        i = start_idx + 1

        while i < len(lines):
            line = lines[i]
            if line.strip() == "":
                method_lines.append(line)
                i += 1
                continue

            current_indent = len(line) - len(line.lstrip())
            if current_indent <= method_indent and line.strip():
                break

            method_lines.append(line)
            i += 1

        return method_lines, i

    def _generate_setup_fixture(
        self,
        setup_method: Optional[List[str]],
        teardown_method: Optional[List[str]],
        base_indent: int,
    ) -> Tuple[List[str], set]:
        """Generate a pytest fixture from setUp/tearDown."""
        result = ["@pytest.fixture", "def setup_test():"]
        instance_properties = set()

        has_setup_code = False
        has_teardown_code = False

        # Add setup code and track self.property assignments
        if setup_method:
            for line in setup_method:
                stripped = line.strip()
                # Skip decorators and def line
                if stripped.startswith("@") or stripped.startswith("def "):
                    continue
                if stripped and not stripped.startswith("pass"):
                    has_setup_code = True
                    # Dedent from method level (base_indent + 8) to function body (4)
                    dedented = self._dedent_line(line, base_indent + 8, target_indent=4)
                    # Convert self. references to local variables
                    converted = re.sub(r"\bself\.(\w+)", r"\1", dedented)
                    result.append(converted)

                    # Track property assignments (self.property = ...)
                    match = re.search(r"\bself\.(\w+)\s*=", line)
                    if match:
                        instance_properties.add(match.group(1))

        if not has_setup_code:
            result.append("    pass")

        # Create a class to hold the properties if any
        if instance_properties:
            result.append("")
            result.append("    # Create object to hold instance properties")
            result.append("    class InstanceProperties:")
            result.append("        pass")
            result.append("")
            result.append("    props = InstanceProperties()")
            for prop in sorted(instance_properties):
                result.append(f"    props.{prop} = {prop}")

        # Add yield
        if instance_properties:
            result.append("    yield props")
        else:
            result.append("    yield")

        # Add teardown code
        if teardown_method:
            for line in teardown_method:
                stripped = line.strip()
                # Skip decorators and def line
                if stripped.startswith("@") or stripped.startswith("def "):
                    continue
                if stripped and not stripped.startswith("pass"):
                    has_teardown_code = True
                    dedented = self._dedent_line(line, base_indent + 8, target_indent=4)
                    # Convert self. references to use props if available
                    if instance_properties:
                        converted = re.sub(r"\bself\.(\w+)", r"props.\1", dedented)
                    else:
                        converted = re.sub(r"\bself\.(\w+)", r"\1", dedented)
                    result.append(converted)

        if not has_teardown_code:
            result.append("    pass")

        return result, instance_properties

    def _generate_class_fixture(
        self,
        setupclass_method: Optional[List[str]],
        teardownclass_method: Optional[List[str]],
        base_indent: int,
    ) -> Tuple[List[str], set]:
        """Generate a pytest module-scoped fixture from setUpClass/tearDownClass."""
        result = ["@pytest.fixture(scope='module')", "def setup_class():"]
        class_properties = set()

        has_setup_code = False
        has_teardown_code = False

        # Add setup code and track cls.property assignments
        if setupclass_method:
            for line in setupclass_method:
                stripped = line.strip()
                # Skip decorators and def line
                if stripped.startswith("@") or stripped.startswith("def "):
                    continue
                if stripped and not stripped.startswith("pass"):
                    has_setup_code = True
                    # Dedent from method level (base_indent + 8) to function body (4)
                    dedented = self._dedent_line(line, base_indent + 8, target_indent=4)
                    # Convert cls. references to local variables
                    converted = re.sub(r"\bcls\.(\w+)", r"\1", dedented)
                    result.append(converted)

                    # Track property assignments (cls.property = ...)
                    match = re.search(r"\bcls\.(\w+)\s*=", line)
                    if match:
                        class_properties.add(match.group(1))

        if not has_setup_code:
            result.append("    pass")

        # Create a class to hold the properties
        if class_properties:
            result.append("")
            result.append("    # Create object to hold class properties")
            result.append("    class ClassProperties:")
            result.append("        pass")
            result.append("")
            result.append("    props = ClassProperties()")
            for prop in sorted(class_properties):
                result.append(f"    props.{prop} = {prop}")

        # Add yield
        if class_properties:
            result.append("    yield props")
        else:
            result.append("    yield")

        # Add teardown code
        if teardownclass_method:
            for line in teardownclass_method:
                stripped = line.strip()
                # Skip decorators and def line
                if stripped.startswith("@") or stripped.startswith("def "):
                    continue
                if stripped and not stripped.startswith("pass"):
                    has_teardown_code = True
                    dedented = self._dedent_line(line, base_indent + 8, target_indent=4)
                    # Convert cls. references to use props if available
                    if class_properties:
                        converted = re.sub(r"\bcls\.(\w+)", r"props.\1", dedented)
                    else:
                        converted = re.sub(r"\bcls\.(\w+)", r"\1", dedented)
                    result.append(converted)

        if not has_teardown_code:
            result.append("    pass")

        return result, class_properties

    def _convert_helper_to_fixture(
        self,
        method_name: str,
        method_params: str,
        method_lines: List[str],
        class_indent: int,
    ) -> List[str]:
        """Convert a helper method to a pytest fixture."""
        result = ["@pytest.fixture", f"def {method_name}_fixture():"]

        has_body = False
        # Convert method body
        for line in method_lines[1:]:  # Skip def line
            if not line.strip():
                if has_body:  # Only add blank lines after we have content
                    result.append(line)
                continue

            has_body = True
            # Dedent from method level (class_indent + 8) to function body (4)
            dedented = self._dedent_line(line, class_indent + 8, target_indent=4)
            converted = self._convert_assertions(dedented)
            converted = self._remove_self_references(converted)
            result.append(converted)

        if not has_body:
            result.append("    pass")

        return result

    def _convert_test_method(
        self,
        method_name: str,
        method_params: str,
        method_lines: List[str],
        class_indent: int,
        fixture_name: Optional[str],
        helper_fixtures: Dict[str, str],
        class_fixture_name: Optional[str] = None,
        class_properties: Optional[set] = None,
        instance_properties: Optional[set] = None,
    ) -> List[str]:
        """Convert a test method to a pytest function."""
        result = []

        # Find where the decorators, def line, and body are in method_lines
        decorators = []
        def_line_idx = None
        method_indent = None

        for idx, line in enumerate(method_lines):
            stripped = line.strip()

            # Check for decorator (could be first line of multi-line decorator)
            if stripped.startswith("@"):
                # This is a decorator - collect it and any continuation lines
                decorator_lines = [line]
                j = idx + 1

                # Check if decorator continues on next lines (not closed yet)
                # Multi-line decorators have unmatched parentheses
                open_parens = line.count("(") - line.count(")")
                while open_parens > 0 and j < len(method_lines):
                    next_line = method_lines[j]
                    decorator_lines.append(next_line)
                    open_parens += next_line.count("(") - next_line.count(")")
                    j += 1

                # Dedent decorator from class method level to module level
                dedented_decorator = []
                for dec_line in decorator_lines:
                    if method_indent is None and dec_line.strip():
                        method_indent = len(dec_line) - len(dec_line.lstrip())
                    dedented = self._dedent_line(
                        dec_line, method_indent, target_indent=0
                    )
                    dedented_decorator.append(dedented)

                decorators.append("\n".join(dedented_decorator))

            elif stripped.startswith("def "):
                # Found the def line
                def_line_idx = idx
                if method_indent is None:
                    method_indent = len(line) - len(line.lstrip())
                break

        # Add decorators
        for decorator in decorators:
            result.append(decorator)

        # Build function signature
        params = []

        # Add other parameters first (excluding self) - these are mock parameters
        if method_params.strip().strip(","):
            other_params = [
                p.strip() for p in method_params.strip(",").split(",") if p.strip()
            ]
            params.extend(other_params)

        # Add instance fixture second
        if fixture_name:
            params.append(fixture_name)

        # Add class fixture last
        if class_fixture_name:
            params.append(class_fixture_name)

        param_str = ", ".join(params) if params else ""
        result.append(f"def {method_name}({param_str}):")

        # Find where the body starts (after the def line, which may be multi-line)
        body_start_idx = def_line_idx + 1
        while (
            body_start_idx < len(method_lines)
            and "):" not in method_lines[body_start_idx - 1]
        ):
            body_start_idx += 1

        has_body = False
        # Convert method body
        for line in method_lines[body_start_idx:]:
            if not line.strip():
                if has_body:  # Only add blank lines after we have content
                    result.append(line)
                continue

            has_body = True
            # Dedent from method level (class_indent + 8) to function body (4)
            dedented = self._dedent_line(line, class_indent + 8, target_indent=4)

            # Convert assertions
            converted = self._convert_assertions(dedented)

            # Convert assertRaises
            converted = self._convert_assert_raises(converted)

            # Convert self.assertRaises to pytest.raises
            converted = re.sub(r"\bself\.assertRaises\(", r"pytest.raises(", converted)

            # Convert self.fail to pytest.fail
            converted = re.sub(r"\bself\.fail\(", r"pytest.fail(", converted)

            # Convert self.<class_property> to setup_class.<property> BEFORE removing self references
            if class_properties and class_fixture_name:
                for prop in class_properties:
                    converted = re.sub(
                        rf"\bself\.{prop}\b", f"{class_fixture_name}.{prop}", converted
                    )

            # Convert self.<instance_property> to setup_test.<property> BEFORE removing self references
            if instance_properties and fixture_name:
                for prop in instance_properties:
                    converted = re.sub(
                        rf"\bself\.{prop}\b", f"{fixture_name}.{prop}", converted
                    )

            # Remove remaining self references
            converted = self._remove_self_references(converted)

            result.append(converted)

        if not has_body:
            result.append("    pass")

        return result

    def _dedent_line(
        self, line: str, remove_indent: int, target_indent: int = 0
    ) -> str:
        """Remove specified amount of indentation and apply target indentation."""
        if not line.strip():
            return ""

        current_indent = len(line) - len(line.lstrip())
        content = line.lstrip()

        # Calculate new indentation
        relative_indent = current_indent - remove_indent
        new_indent = target_indent + max(0, relative_indent)

        return " " * new_indent + content

    def _convert_assertions(self, line: str) -> str:
        """Convert unittest assertions to pytest assertions."""
        # Handle assertRaises separately (it's a context manager)
        if "self.assertRaises" in line:
            line = re.sub(
                r"with\s+self\.assertRaises\((.*?)\)", r"with pytest.raises(\1)", line
            )
            line = re.sub(r"self\.assertRaises\((.*?)\)", r"pytest.raises(\1)", line)
            return line

        # Handle assertRaisesRegex
        if "self.assertRaisesRegex" in line:
            line = re.sub(
                r"self\.assertRaisesRegex\((.*?),\s*(.*?)\)",
                r"pytest.raises(\1, match=\2)",
                line,
            )
            return line

        # Handle assertEqual and assertNotEqual specially - they need operator replacement
        if "self.assertEqual(" in line:
            line = self._convert_assert_equal(line, "==")
        elif "self.assertNotEqual(" in line:
            line = self._convert_assert_equal(line, "!=")
        else:
            # Apply other assertion conversions
            for pattern, replacement in self.ASSERTION_MAP.items():
                if pattern.endswith("\\(") and pattern in line:
                    continue  # Skip assertEqual/assertNotEqual patterns
                line = re.sub(pattern, replacement, line)

        return line

    def _convert_assert_equal(self, line: str, operator: str) -> str:
        """Convert assertEqual/assertNotEqual to assert with proper operator."""
        # Find the assertion call
        if operator == "==":
            match = re.search(r"self\.assertEqual\((.*)\)", line)
        else:
            match = re.search(r"self\.assertNotEqual\((.*)\)", line)

        if not match:
            return line

        args_str = match.group(1)

        # Simple split by comma (this handles most cases)
        # For complex cases with nested function calls, we need to be smarter
        args = self._smart_split_args(args_str)

        if len(args) >= 2:
            arg1 = args[0].strip()
            arg2 = args[1].strip()

            # Get the indentation and prefix
            prefix = line[: line.index("self.")]

            return f"{prefix}assert {arg1} {operator} {arg2}"

        return line

    def _smart_split_args(self, args_str: str) -> List[str]:
        """Split function arguments by comma, respecting nested parentheses and brackets."""
        args = []
        current_arg = []
        depth = 0

        for char in args_str:
            if char in "([{":
                depth += 1
                current_arg.append(char)
            elif char in ")]}":
                depth -= 1
                current_arg.append(char)
            elif char == "," and depth == 0:
                args.append("".join(current_arg))
                current_arg = []
            else:
                current_arg.append(char)

        # Add the last argument
        if current_arg:
            args.append("".join(current_arg))

        return args

    def _convert_assert_raises(self, line: str) -> str:
        """Additional assertRaises conversions (already handled in _convert_assertions)."""
        return line

    def _remove_self_references(self, line: str) -> str:
        """Remove self. references and self parameters."""
        # Remove self. prefix (but not in strings)
        # Simple approach: replace self. with empty string
        line = re.sub(r"\bself\.", "", line)

        # Remove self parameter from function definitions (shouldn't be in converted code)
        line = re.sub(r"\(self,\s*", "(", line)
        line = re.sub(r"\(self\)", "()", line)

        return line


def convert_file(file_path: Path, backup: bool = True, dry_run: bool = False) -> bool:
    """
    Convert a single test file.

    Args:
        file_path: Path to the test file
        backup: Whether to create a backup
        dry_run: If True, only show what would be done

    Returns:
        True if conversion was successful, False otherwise
    """
    try:
        content = file_path.read_text()

        # Check if file contains TestCase
        if "TestCase" not in content:
            print(f"Skipping {file_path}: No TestCase found")
            return False

        print(f"Converting {file_path}...")

        converter = TestConverter(content)
        converted = converter.convert()

        if dry_run:
            print(f"\n{'='*60}")
            print(f"DRY RUN - Would convert {file_path}")
            print(f"{'='*60}")
            print(converted)
            print(f"{'='*60}\n")
            return True

        # Create backup
        if backup:
            backup_path = file_path.with_suffix(".py.unittest.bak")
            backup_path.write_text(content)
            print(f"  Created backup: {backup_path}")

        # Write converted content
        file_path.write_text(converted)
        print("  ✓ Converted successfully")
        return True

    except Exception as e:
        print(f"Error converting {file_path}: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Convert unittest test files to pytest format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert a single file with dry-run
  %(prog)s tests/test_example.py --dry-run

  # Convert a single file
  %(prog)s tests/test_example.py

  # Convert all files in a directory
  %(prog)s tests/ --recursive

  # Convert without creating backups
  %(prog)s tests/ --recursive --no-backup
        """,
    )
    parser.add_argument("path", type=Path, help="Test file or directory to convert")
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Recursively convert all test files in directory",
    )
    parser.add_argument(
        "--no-backup", action="store_true", help="Do not create backup files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )

    args = parser.parse_args()

    if not args.path.exists():
        print(f"Error: {args.path} does not exist")
        sys.exit(1)

    files_to_convert = []

    if args.path.is_file():
        files_to_convert.append(args.path)
    elif args.path.is_dir():
        if args.recursive:
            files_to_convert = list(args.path.rglob("test_*.py"))
        else:
            files_to_convert = list(args.path.glob("test_*.py"))
    else:
        print(f"Error: {args.path} is not a file or directory")
        sys.exit(1)

    if not files_to_convert:
        print(f"No test files found in {args.path}")
        sys.exit(0)

    print(f"Found {len(files_to_convert)} test file(s) to process\n")

    success_count = 0
    for file_path in files_to_convert:
        if convert_file(file_path, backup=not args.no_backup, dry_run=args.dry_run):
            success_count += 1

    print(f"\n{'='*60}")
    print(
        f"Conversion complete: {success_count}/{len(files_to_convert)} files converted"
    )
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
