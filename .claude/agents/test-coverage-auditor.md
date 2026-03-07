---
name: test-coverage-auditor
description: Audits structural parity between src/heliotrace/ and tests/ — lists any src/ module files that lack a corresponding test file.
---
1. List all .py files under src/heliotrace/ (excluding __init__.py and __pycache__).
2. For each file src/heliotrace/X/Y.py, check if tests/X/test_Y.py exists.
3. Report missing test files as: MISSING: src/heliotrace/X/Y.py → expected tests/X/test_Y.py
4. Report a summary count: "N/M modules covered".
