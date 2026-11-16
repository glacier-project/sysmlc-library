"""SysML v2 and KerML libraries for sysmlc."""

from pathlib import Path

__version__ = "0.1.0"

_PACKAGE_DIR = Path(__file__).resolve().parent
_LIBRARY_SUFFIXES = (".kerml", ".sysml")


def library_files() -> list[str]:
    """Absolute paths of every library file this package ships.

    Registered under the ``sysmlc.libraries`` entry-point group. Any
    ``.kerml`` or ``.sysml`` file in the package directory is a library.

    Returns:
        The sorted library file paths as strings.
    """
    return sorted(
        str(path)
        for path in _PACKAGE_DIR.iterdir()
        if path.suffix in _LIBRARY_SUFFIXES
    )
