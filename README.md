# sysmlc-library

SysML v2 and KerML libraries for sysmlc. Installing sysmlc installs this
package, and sysmlc loads every library in it automatically through the
`sysmlc.libraries` entry point. The files also work from any editor: see
Editor setup. The package has no dependency on sysmlc.

## Libraries

### FixedWidthScalarValues

Fixed-width numeric features (`int8` ... `uint64`, `float32`, `float64`)
whose ranges follow C's `<stdint.h>`. The library defines attribute usages to
subset, not datatypes:

```sysml
private import FixedWidthScalarValues::*;
attribute count :> uint8 := 0;
```

Plain literals and arithmetic type-check without casts. Each feature carries
its range as an invariant, which subsetting attributes inherit.

Widths go on attributes, not on a quantity's `num` (sysmlc ignores it there).

## Editor setup

Point Syside at a library file in `syside.toml` with a `./`-prefixed relative
path (`../lib` does not work):

```toml
include = ["./path/to/sysmlc_library/FixedWidthScalarValues.kerml"]
```

## Versioning

Semantic versions. Library elements are only ever added, never renamed or
removed.
