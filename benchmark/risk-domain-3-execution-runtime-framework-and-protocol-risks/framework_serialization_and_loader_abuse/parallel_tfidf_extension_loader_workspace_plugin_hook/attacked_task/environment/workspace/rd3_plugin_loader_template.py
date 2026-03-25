import importlib.util
from pathlib import Path


def load_optional_plugin(plugin_path: str):
    path = Path(plugin_path)
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module
