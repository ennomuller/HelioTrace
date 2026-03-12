# Architectural Principles

1. **Design for Deep Modules**: Keep public APIs (exported in `__init__.py`) minimal. Hide complex internal implementations. If a module's API is larger than its functionality, the abstraction is too shallow.
2. **Enforce Unidirectional Dependencies**: Lower-level, foundational modules (e.g., utils, logic) must never import from higher-level, application-specific modules (e.g., UI, CLI).
3. **Maintain Structural Parity**: Every functional file in `src/` must have a corresponding, descriptive test file in `tests/` using the same directory hierarchy.
