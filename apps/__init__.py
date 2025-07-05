"""
Namespace package marker for the monorepo-level `apps` directory.

This file ensures that Python recognises `apps` as a proper package so
that imports such as `import apps.backend` succeed.  Without this
marker, the CI Import Sanity Guard would fail with:

    ModuleNotFoundError: No module named 'apps'

Do **not** place application logic here – this file must remain lean to
avoid unintended side-effects during the early import phase.
""" 