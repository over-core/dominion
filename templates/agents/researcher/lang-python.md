# Python Research Patterns

When researching Python projects:

- Use `pyproject.toml` / `setup.py` for dependency analysis
- Check for type hints coverage — indicates project maturity
- Note test framework: pytest (standard), unittest, hypothesis (property-based)
- Check for async patterns: asyncio, FastAPI, aiohttp
- Identify ORM: SQLAlchemy, Django ORM, Tortoise
- Check formatter/linter: ruff, black, flake8, mypy, pyright

## Python-Specific Risks

- Dependency conflicts between packages with incompatible version constraints
- Import cycles in deeply nested packages
- Missing type annotations in public APIs
- Global mutable state in module-level variables
