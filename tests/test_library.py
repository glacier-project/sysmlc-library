import os
import subprocess
import zipfile
from importlib.metadata import entry_points
from pathlib import Path

import pytest

from sysmlc_library import __version__, library_files

PACKAGE_DIR = Path(__file__).resolve().parent.parent

EXPECTED: dict[str, tuple[int, int] | None] = {
    "int8": (-128, 127),
    "int16": (-32768, 32767),
    "int32": (-2147483648, 2147483647),
    "int64": (-9223372036854775808, 9223372036854775807),
    "uint8": (0, 255),
    "uint16": (0, 65535),
    "uint32": (0, 4294967295),
    "uint64": (0, 18446744073709551615),
    "float32": None,
    "float64": None,
}

needs_license = pytest.mark.skipif(
    not os.environ.get("SYSIDE_LICENSE_KEY"),
    reason="SYSIDE_LICENSE_KEY is not set",
)


def test_library_files_returns_the_kerml_file() -> None:
    paths = library_files()
    assert [Path(p).name for p in paths] == ["FixedWidthScalarValues.kerml"]
    assert all(Path(p).is_absolute() and Path(p).is_file() for p in paths)


def test_entry_point_is_registered() -> None:
    eps = [
        e
        for e in entry_points(group="sysmlc.libraries")
        if e.name == "sysmlc_library"
    ]
    assert [e.value for e in eps] == ["sysmlc_library:library_files"]
    # guards against stale installed metadata
    assert eps[0].load()() == library_files()


@needs_license
def test_library_loads_without_diagnostics() -> None:
    import syside

    _, diagnostics = syside.try_load_model(paths=library_files())
    assert list(diagnostics.all) == []


@needs_license
def test_ranges_match_the_documented_table() -> None:
    import syside

    model, _ = syside.try_load_model(paths=library_files())
    ranges = _read_ranges(model)
    assert ranges == EXPECTED


@needs_license
def test_integers_fit_in_signed_64_bits() -> None:
    """Tools that read Syside's JSON (such as the visualizer) reject larger ones."""
    import json

    import syside

    model, _ = syside.try_load_model(paths=library_files())
    options = syside.SerializationOptions.minimal()
    for document in model.documents:
        with document.lock() as root:
            exported = json.loads(syside.json.dumps(root.root_node, options))
        too_big = [n for n in _integers(exported) if not -(2**63) <= n < 2**63]
        assert too_big == []


def _integers(value: object) -> list[int]:
    if isinstance(value, bool):
        return []
    if isinstance(value, int):
        return [value]
    if isinstance(value, dict):
        value = list(value.values())
    if isinstance(value, list):
        return [n for item in value for n in _integers(item)]
    return []


def _integer_bound(expr: object) -> int:
    """Evaluate an integer bound: a literal, or literals joined by + - *."""
    import syside

    if isinstance(expr, syside.LiteralInteger):
        return expr.value
    assert isinstance(expr, syside.OperatorExpression)
    operands = [_integer_bound(o) for o in expr.operands.collect()]
    if expr.operator == syside.Operator.Minus:
        return -operands[0] if len(operands) == 1 else operands[0] - operands[1]
    if expr.operator == syside.Operator.Plus:
        return operands[0] + operands[1]
    assert expr.operator == syside.Operator.Multiply
    return operands[0] * operands[1]


def _collect_bounds(expr: object, bounds: dict[str, int]) -> None:
    """Gather `>=`/`<=` literal bounds from a conjunction of comparisons."""
    import syside

    assert isinstance(expr, syside.OperatorExpression)
    operands = expr.operands.collect()
    if expr.operator == syside.Operator.LogicalAnd:
        for operand in operands:
            _collect_bounds(operand, bounds)
        return
    assert expr.operator in (
        syside.Operator.GreaterEqual,
        syside.Operator.LessEqual,
    )
    assert len(operands) == 2
    bounds[str(expr.operator)] = _integer_bound(operands[1])


def _read_ranges(model: object) -> dict[str, tuple[int, int] | None]:
    import syside

    assert isinstance(model, syside.Model)
    ranges: dict[str, tuple[int, int] | None] = {}
    for document in model.documents:
        with document.lock() as root:
            (package,) = root.root_node.owned_members.collect()
            assert isinstance(package, syside.Package)
            assert package.name == "FixedWidthScalarValues"
            for feature in package.owned_members.collect():
                if not isinstance(feature, syside.Feature):
                    continue
                assert feature.name is not None
                invariants = [
                    m
                    for m in feature.owned_members.collect()
                    if isinstance(m, syside.Invariant)
                ]
                if not invariants:
                    ranges[feature.name] = None
                    continue
                (invariant,) = invariants
                bounds: dict[str, int] = {}
                _collect_bounds(invariant.result_expression, bounds)
                lower = str(syside.Operator.GreaterEqual)
                upper = str(syside.Operator.LessEqual)
                assert upper in bounds, f"{feature.name} has no upper bound"
                # Natural-typed features carry no lower bound in their
                # invariant: their lower bound 0 comes from Natural itself.
                if lower not in bounds:
                    assert feature.name.startswith("uint"), (
                        f"{feature.name} has no lower bound"
                    )
                ranges[feature.name] = (bounds.get(lower, 0), bounds[upper])
    return ranges


def test_wheel_ships_the_kerml(tmp_path: Path) -> None:
    subprocess.run(
        ["uv", "build", "--wheel", "-o", str(tmp_path)],
        cwd=PACKAGE_DIR,
        check=True,
        capture_output=True,
    )
    (wheel,) = tmp_path.glob(f"sysmlc_library-{__version__}-*.whl")
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
    assert "sysmlc_library/FixedWidthScalarValues.kerml" in names
