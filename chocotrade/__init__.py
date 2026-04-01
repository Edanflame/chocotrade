"""
构造函数
"""

# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0

import importlib

from ._version import __version__

# 延迟加载 my_module，避免 circular import
try:
    my_module = importlib.import_module(".src.my_module1", package=__name__)

    __all__ = ["my_module", "__version__"]

except ModuleNotFoundError:
    __all__ = ["__version__"]
