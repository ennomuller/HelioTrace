---
name: gen-test
description: Scaffold a pytest test file for a given src/heliotrace module, matching the tests/ directory hierarchy and the project's structural parity rule.
---
The user will provide a module path like `src/heliotrace/physics/drag.py`.

1. Read the source file and identify all public functions/classes (no leading underscore).
2. Determine the mirror path: `src/heliotrace/X/Y.py` → `tests/X/test_Y.py`.
3. Create the test file with:
   - One `test_<function>_<scenario>` function per public function
   - Import the module under test
   - Use `pytest.approx` for float comparisons
   - Mark physics-critical tests with a `# PHYSICS:` comment explaining what invariant is checked
4. Do not add fixtures unless clearly needed — keep it minimal.
