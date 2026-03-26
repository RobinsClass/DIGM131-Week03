"""
DIGM 131 - Assignment 3: Function Library + Scene
Self-Check Unit Tests

Run this file from your assignment folder:
    python test_assignment.py

These tests check your code's STRUCTURE without running it (no Maya needed).
They help you catch common issues before submitting. Good luck!
"""

import ast
import os
import re
import sys
import unittest


FUNCTIONS_FILE = "scene_functions.py"
MAIN_FILE = "main_scene.py"


def get_file_path(filename):
    """Return the absolute path to a file in the same directory as this test."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


def read_source(filename):
    """Read a file as plain text."""
    path = get_file_path(filename)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def parse_file_ast(filename):
    """Parse a file into an AST tree."""
    source = read_source(filename)
    if source is None:
        return None
    try:
        return ast.parse(source)
    except SyntaxError:
        return None


def get_function_defs(tree):
    """Return a list of all top-level FunctionDef nodes in the AST."""
    if tree is None:
        return []
    return [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]


def get_docstring(func_node):
    """Extract the docstring from a function node, or return None."""
    if (func_node.body
            and isinstance(func_node.body[0], ast.Expr)
            and isinstance(func_node.body[0].value, ast.Constant)):
        val = func_node.body[0].value
        return val.value if isinstance(val.value, str) else None
    return None


def has_return(func_node):
    """Check if a function contains a return statement with a value."""
    for node in ast.walk(func_node):
        if isinstance(node, ast.Return) and node.value is not None:
            return True
    return False


class TestAssignment03(unittest.TestCase):
    """Tests for Assignment 3 - Function Library + Scene."""

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _require_source(self, filename):
        source = read_source(filename)
        self.assertIsNotNone(
            source,
            f"Could not find '{filename}'. Make sure it exists in the same\n"
            f"  folder as this test."
        )
        return source

    def _require_tree(self, filename):
        tree = parse_file_ast(filename)
        self.assertIsNotNone(
            tree,
            f"'{filename}' has a SyntaxError or does not exist.\n"
            f"  Open it in your editor and fix any errors first!"
        )
        return tree

    # ------------------------------------------------------------------
    # Multi-file helpers
    # ------------------------------------------------------------------
    def _require_source_for(self, filename):
        source = read_source(filename)
        self.assertIsNotNone(
            source,
            f"Could not find '{filename}'. Make sure it exists in the same\n"
            f"  folder as this test."
        )
        return source

    def _require_tree_for(self, filename):
        tree = parse_file_ast(filename)
        self.assertIsNotNone(
            tree,
            f"'{filename}' has a SyntaxError or does not exist.\n"
            f"  Open it in your editor and fix any errors first!"
        )
        return tree

    # ------------------------------------------------------------------
    # Tests
    # ------------------------------------------------------------------
    def test_todos_completed(self):
        """Check that you've replaced all TODO placeholders with your own code in both files."""
        for filename in [FUNCTIONS_FILE, MAIN_FILE]:
            source = self._require_source_for(filename)
            todo_count = len(re.findall(r'#\s*TODO', source))
            self.assertEqual(
                todo_count, 0,
                f"Found {todo_count} TODO comment(s) still in '{filename}'.\n"
                f"  Replace each TODO section with your own code."
            )

    def test_no_pass_only_functions(self):
        """Check that functions have real implementations, not just 'pass', in both files."""
        for filename in [FUNCTIONS_FILE, MAIN_FILE]:
            tree = self._require_tree_for(filename)
            pass_only = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    body = node.body
                    real_body = body
                    if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0].value, 'value', None), str):
                        real_body = body[1:]
                    if len(real_body) == 0 or (len(real_body) == 1 and isinstance(real_body[0], ast.Pass)):
                        pass_only.append(node.name)
            self.assertEqual(
                len(pass_only), 0,
                f"These functions in '{filename}' are still empty (just 'pass'):\n"
                f"  {', '.join(pass_only)}\n"
                f"  Add your implementation to each one!"
            )

    def test_functions_have_cmds_calls(self):
        """Check that functions in scene_functions.py contain actual Maya cmds calls."""
        tree = self._require_tree_for(FUNCTIONS_FILE)
        source = self._require_source_for(FUNCTIONS_FILE)
        funcs = get_function_defs(tree)
        empty_funcs = []
        for f in funcs:
            # Get the source lines for this function
            func_has_cmds = False
            for node in ast.walk(f):
                if isinstance(node, ast.Attribute):
                    if isinstance(node.value, ast.Name) and node.value.id in ("cmds", "mc"):
                        func_has_cmds = True
                        break
            if not func_has_cmds:
                empty_funcs.append(f.name)
        self.assertEqual(
            len(empty_funcs), 0,
            f"These functions in '{FUNCTIONS_FILE}' don't call any cmds commands:\n"
            f"  {', '.join(empty_funcs)}\n"
            f"  Each function should use maya.cmds to create or modify objects."
        )

    def test_both_files_exist_and_parse(self):
        """Check that both scene_functions.py and main_scene.py exist and have no syntax errors."""
        for fname in [FUNCTIONS_FILE, MAIN_FILE]:
            path = get_file_path(fname)
            self.assertTrue(
                os.path.exists(path),
                f"'{fname}' not found. Did you name it correctly?"
            )
            source = read_source(fname)
            try:
                ast.parse(source)
            except SyntaxError as e:
                self.fail(
                    f"'{fname}' has a SyntaxError on line {e.lineno}: {e.msg}"
                )

    def test_scene_functions_has_five_or_more_functions(self):
        """Check that scene_functions.py defines at least 5 functions."""
        tree = self._require_tree(FUNCTIONS_FILE)
        funcs = get_function_defs(tree)
        self.assertGreaterEqual(
            len(funcs), 5,
            f"Found only {len(funcs)} function(s) in '{FUNCTIONS_FILE}'.\n"
            f"  You need at least 5 reusable functions in your library.\n"
            f"  Think about different objects or transformations in your scene."
        )

    def test_all_functions_have_docstrings(self):
        """Check that every function in scene_functions.py has a docstring."""
        tree = self._require_tree(FUNCTIONS_FILE)
        funcs = get_function_defs(tree)
        missing = [f.name for f in funcs if get_docstring(f) is None]
        self.assertEqual(
            len(missing), 0,
            f"These functions are missing docstrings: {missing}\n"
            f"  Every function needs a docstring right after the def line:\n"
            f'    def create_tree(height):\n'
            f'        """Create a tree with the given height."""\n'
            f'        ...'
        )

    def test_docstrings_have_args_section(self):
        """Check that functions with parameters document them with an Args: section."""
        tree = self._require_tree(FUNCTIONS_FILE)
        funcs = get_function_defs(tree)
        missing_args = []

        for f in funcs:
            # Get parameter names (skip 'self')
            params = [a.arg for a in f.args.args if a.arg != "self"]
            if not params:
                continue
            doc = get_docstring(f)
            if doc and "args:" not in doc.lower():
                missing_args.append(f.name)

        self.assertEqual(
            len(missing_args), 0,
            f"These functions have parameters but no 'Args:' section in their docstring:\n"
            f"  {missing_args}\n"
            f"  Document your parameters like this:\n"
            f'    def create_tree(height, radius):\n'
            f'        """Create a tree.\n'
            f"\n"
            f"        Args:\n"
            f"            height: How tall the tree should be.\n"
            f'            radius: The radius of the trunk.\n'
            f'        """'
        )

    def test_docstrings_have_returns_section(self):
        """Check that functions with return values document them with a Returns: section."""
        tree = self._require_tree(FUNCTIONS_FILE)
        funcs = get_function_defs(tree)
        missing_returns = []

        for f in funcs:
            if not has_return(f):
                continue
            doc = get_docstring(f)
            if doc and "returns:" not in doc.lower() and "return:" not in doc.lower():
                missing_returns.append(f.name)

        self.assertEqual(
            len(missing_returns), 0,
            f"These functions return a value but have no 'Returns:' section:\n"
            f"  {missing_returns}\n"
            f"  Document what your function returns:\n"
            f"    Returns:\n"
            f"        The name of the created object."
        )

    def test_main_imports_scene_functions(self):
        """Check that main_scene.py imports from scene_functions."""
        source = self._require_source(MAIN_FILE)
        has_import = bool(
            re.search(r"from\s+scene_functions\s+import", source)
            or re.search(r"import\s+scene_functions", source)
        )
        self.assertTrue(
            has_import,
            f"'{MAIN_FILE}' should import from '{FUNCTIONS_FILE}'.\n"
            f"  For example:\n"
            f"    from scene_functions import create_tree, create_rock\n"
            f"  or:\n"
            f"    import scene_functions"
        )

    def test_no_code_duplication(self):
        """Check that there are no 3+ consecutive identical non-trivial lines (avoid copy-paste)."""
        source = self._require_source(FUNCTIONS_FILE)
        lines = source.split("\n")
        duplicated = []

        for i in range(len(lines) - 2):
            line = lines[i].strip()
            # Skip blank lines and trivial lines
            if not line or line.startswith("#") or len(line) < 10:
                continue
            if lines[i].strip() == lines[i + 1].strip() == lines[i + 2].strip():
                duplicated.append((i + 1, line))

        self.assertEqual(
            len(duplicated), 0,
            f"Found duplicate consecutive lines (possible copy-paste):\n"
            + "\n".join(f"  Line {ln}: {text[:60]}" for ln, text in duplicated[:3])
            + "\n  If you're repeating code, consider making it a function\n"
            + "  with parameters instead!"
        )

    def test_function_names_are_snake_case(self):
        """Check that all function names follow snake_case convention (e.g., create_tree, not CreateTree)."""
        tree = self._require_tree(FUNCTIONS_FILE)
        funcs = get_function_defs(tree)
        bad_names = []

        snake_case_pattern = re.compile(r"^[a-z_][a-z0-9_]*$")
        for f in funcs:
            if not snake_case_pattern.match(f.name):
                bad_names.append(f.name)

        self.assertEqual(
            len(bad_names), 0,
            f"These function names are not snake_case: {bad_names}\n"
            f"  Python convention: use lowercase with underscores.\n"
            f"  'CreateTree' -> 'create_tree'\n"
            f"  'makeRock' -> 'make_rock'"
        )

    def test_functions_are_used_in_main(self):
        """Check that main_scene.py actually calls functions (not just imports them)."""
        tree = self._require_tree(MAIN_FILE)
        calls = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.Call)
        ]
        # Filter out built-in/common calls to count meaningful ones
        self.assertGreaterEqual(
            len(calls), 3,
            f"'{MAIN_FILE}' has very few function calls.\n"
            f"  Your main scene should use the functions from your library\n"
            f"  to build a scene. Call your functions to create objects!"
        )


# ======================================================================
# Friendly summary
# ======================================================================
class FriendlySummary(unittest.TestResult):
    """Custom test result that prints a friendly summary at the end."""

    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.stream = stream
        self.successes = 0
        self.total = 0

    def startTest(self, test):
        super().startTest(test)
        self.total += 1

    def addSuccess(self, test):
        super().addSuccess(test)
        self.successes += 1
        self.stream.write(f"  PASS: {test.shortDescription()}\n")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.stream.write(f"  FAIL: {test.shortDescription()}\n")
        msg = str(err[1])
        for line in msg.split("\n"):
            self.stream.write(f"        {line}\n")
        self.stream.write("\n")

    def addError(self, test, err):
        super().addError(test, err)
        self.stream.write(f"  ERROR: {test.shortDescription()}\n")
        self.stream.write(f"        {err[1]}\n\n")

    def printSummary(self):
        self.stream.write("\n" + "=" * 60 + "\n")
        self.stream.write(f"  Score: {self.successes}/{self.total} checks passed\n")
        if self.successes == self.total:
            self.stream.write("  Excellent! All checks passed!\n")
        elif self.successes >= self.total - 2:
            self.stream.write("  Nearly there! Just a few tweaks needed.\n")
        else:
            self.stream.write("  Keep going -- good functions take practice!\n")
        self.stream.write("=" * 60 + "\n")


class FriendlyRunner(unittest.TextTestRunner):
    """Test runner that uses the friendly summary."""

    def run(self, test):
        result = FriendlySummary(sys.stdout, True, self.verbosity)
        sys.stdout.write("\n" + "=" * 60 + "\n")
        sys.stdout.write("  Assignment 3: Function Library + Scene - Self-Check\n")
        sys.stdout.write("=" * 60 + "\n\n")
        test(result)
        result.printSummary()
        return result


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestAssignment03)
    runner = FriendlyRunner()
    result = runner.run(suite)
    # Exit with non-zero code if any tests failed (for CI/autograding)
    sys.exit(0 if result.successes == result.total else 1)
