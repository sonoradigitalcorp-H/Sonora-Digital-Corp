"""
Deprecated: truth/ has been migrated to constitution/ (HAS-001).
Run tests/test_constitution.py instead.
The symlink truth/ → constitution/ exists for backward compat.
"""
import warnings
warnings.warn(
    "test_truth.py is deprecated. Use tests/test_constitution.py (HAS-001).",
    DeprecationWarning, stacklevel=2
)

# Delegate to new tests
from tests.test_constitution import *  # noqa: F401, F403
