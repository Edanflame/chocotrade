import importlib
import importlib.util
import sys
from importlib import resources

from .config import settings


def safe_import_module(module_name):
    """"""
    if module_name in sys.modules:
        return sys.modules[module_name]

    # pkg_relative_path = f".plugins.{module_name}"
    pkg_relative_path = f".gateways.{module_name}"

    parent_package = __name__.rpartition('.')[0]
    return importlib.import_module(pkg_relative_path, package=parent_package)
    try:
        parent_package = __name__.rpartition('.')[0]
        return importlib.import_module(pkg_relative_path, package=parent_package)
    except (ImportError, ValueError):
        pass

    plugins_dir = settings.base_dir / "plugins"
    target_file = plugins_dir / f"{module_name}.py"

    if target_file.exists():
        try:
            file_dir = str(target_file.parent)
            if file_dir not in sys.path:
                sys.path.insert(0, file_dir) # 临时加入搜索路径

            spec = importlib.util.spec_from_file_location(module_name, str(target_file))
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)

                sys.modules[module_name] = module

                spec.loader.exec_module(module)
                return module
        except Exception:
            pass

    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError:
        pass

    raise ImportError(f"模块 {module_name} 彻底找不到了。")


def load_source(*args):
    """"""
    resource_path = resources.files("chocotrade").joinpath(*args)
    return resource_path

