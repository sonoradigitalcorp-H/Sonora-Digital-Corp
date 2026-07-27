"""
Deprecated: truth/ has been migrated to kernel/ (HAS-001).
Run tests/test_constitution.py instead.
"""
import warnings
warnings.warn(
    "test_truth.py is deprecated. Use tests/test_constitution.py (HAS-001).",
    DeprecationWarning, stacklevel=2
)

# Delegate to new tests
from tests.test_constitution import *  # noqa: F401, F403
