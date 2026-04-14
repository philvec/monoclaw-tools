import importlib
import pkgutil
from pathlib import Path

for _mod in pkgutil.iter_modules([str(Path(__file__).parent)]):
    importlib.import_module(f"tools.{_mod.name}")
