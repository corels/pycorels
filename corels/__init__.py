from .corels import CorelsClassifier
from .utils import load_from_csv, RuleList

__version__ = "1.1.12"
with open("VERSION.txt") as f:
    __version__ = f.read()

__all__ = ["CorelsClassifier", "load_from_csv", "RuleList"]
