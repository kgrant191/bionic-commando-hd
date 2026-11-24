"""Rebuild the v1.0.0 Mesen IPS for the headered Bionic Commando (USA) ROM."""
import argparse
from pathlib import Path


def display_changes():
    # Each digit occupies a native metasprite. One hardware sprite now anchors
    # the HD glyph. The pack reconstructs its original shape from the atlas.
    digit_offsets = (
        0x2A947, 0x2A970, 0x2A981, 0x2A9AE, 0x2A9D3,
        0x2A9F4, 0x2AA21, 0x2AA4E, 0x2AA67, 0x2AA94,
    )
    for digit, offset in enumerate(digit_offsets):
        yield offset, bytes([1, 0xFE - digit, 0, 0, 1])

    # The side-view rocket shares its old CHR tile with other effects. Give
    # its four quadrants a private marker and retain their native positions.
    yield 0x204E0, bytes.fromhex("0000000000000001 0000000000000001")
    yield 0x284B8, bytes.fromhex("04 4D F8 F8 81  4D F8 00 01  4D 00 F8 C1  4D 00 00 41")

    # Two call sites, both in the rooftop NPC routine, enter these wrappers.
    # The native pose initialization and facing store run before the common
    # test. Bit 3 controls native sprite drawing. The replacement artwork is
    # attached to world coordinates and follows the original facing byte.
    rooftop_wrapper = bytes.fromhex(
        "20 B0 B5 "  # $FFB6  JSR $B5B0        original pose initializer
        "4C BF FF "  #        JMP $FFBF        common display test
        "9D 33 06 "  # $FFBC  STA $0633,X      original facing store
        "A5 4D "     # $FFBF  LDA $4D          area
        "C9 12 "     #        CMP #$12         Area 18
        "D0 11 "     #        BNE return
        "E0 0B "     #        CPX #$0B         first rooftop NPC
        "F0 04 "     #        BEQ hide
        "E0 0D "     #        CPX #$0D         second rooftop NPC
        "D0 09 "     #        BNE return
        "BD A6 06 "  # hide   LDA $06A6,X
        "29 F7 "     #        AND #$F7
        "9D A6 06 "  #        STA $06A6,X
        "60 60"      #        RTS / return: RTS
    )
    yield 0x3FFC6, rooftop_wrapper
    yield 0x3F866, bytes.fromhex("20 B6 FF")
    yield 0x3F877, bytes.fromhex("20 BC FF")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    output = parser.parse_args().output
    patch = bytearray(b"PATCH")
    for offset, data in display_changes():
        patch.extend(offset.to_bytes(3, "big"))
        patch.extend(len(data).to_bytes(2, "big"))
        patch.extend(data)
    patch.extend(b"EOF")
    output.write_bytes(patch)


if __name__ == "__main__":
    main()
