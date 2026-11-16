library package FixedWidthScalarValues {
    doc /* Fixed-width numeric features for embedded targets. Subset them:
         * `attribute count :> uint8 := 0;`. Ranges follow C's <stdint.h>. */
    private import ScalarValues::*;

    feature int8 : Integer[1] {
        doc /* Signed 8-bit integer. */
        inv int8Range { that >= -128 and that <= 127 }
    }

    feature int16 : Integer[1] {
        doc /* Signed 16-bit integer. */
        inv int16Range { that >= -32768 and that <= 32767 }
    }

    feature int32 : Integer[1] {
        doc /* Signed 32-bit integer. */
        inv int32Range { that >= -2147483648 and that <= 2147483647 }
    }

    feature int64 : Integer[1] {
        doc /* Signed 64-bit integer. */
        inv int64Range { that >= -9223372036854775808 and that <= 9223372036854775807 }
    }

    feature uint8 : Natural[1] {
        doc /* Unsigned 8-bit integer. */
        inv uint8Range { that <= 255 }
    }

    feature uint16 : Natural[1] {
        doc /* Unsigned 16-bit integer. */
        inv uint16Range { that <= 65535 }
    }

    feature uint32 : Natural[1] {
        doc /* Unsigned 32-bit integer. */
        inv uint32Range { that <= 4294967295 }
    }

    feature uint64 : Natural[1] {
        doc /* Unsigned 64-bit integer. */
        inv uint64Range { that <= 18446744073709551615 }
    }

    feature float32 : Real[1] {
        doc /* IEEE 754 single-precision values. */
    }

    feature float64 : Real[1] {
        doc /* IEEE 754 double-precision values. */
    }
}
