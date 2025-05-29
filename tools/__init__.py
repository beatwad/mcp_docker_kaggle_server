"""Tools package initialization.

This module exports the API instance and tool initialization functions
to avoid circular import issues.
"""

from tools.auth import init_auth_tools, api, ensure_authenticated
from tools.competitions import init_competition_tools
from tools.datasets import init_dataset_tools
from tools.kernels import init_kernel_tools
from tools.models import init_model_tools
from tools.config import init_config_tools

__all__ = [
    "init_auth_tools",
    "init_competition_tools",
    "init_dataset_tools",
    "init_kernel_tools",
    "init_model_tools",
    "init_config_tools",
    "api",
    "ensure_authenticated",
]
