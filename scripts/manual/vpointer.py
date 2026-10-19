"""A virtual pointer for the headless sway, driven one command per line on stdin.

    python vpointer.py PROTO_DIR WIDTH HEIGHT

PROTO_DIR holds the `vpproto` package that pywayland's scanner generated from wayland.xml
and wlr-virtual-pointer-unstable-v1.xml; WIDTH and HEIGHT are the output layout's size in
logical px. Commands: `move X Y` (absolute, logical px), `press`, `release`. Each is
answered with `ok` once sent.

wlrctl creates a new virtual pointer for every command, so a press never reaches the
surface the previous move entered; drags need one pointer that lives across the whole
gesture. Absolute motion also sidesteps pointer acceleration.
"""

import os
import sys
import time

sys.path.insert(0, sys.argv[1])

from pywayland.client import Display  # noqa: E402
from vpproto.wayland import WlSeat  # noqa: E402
from vpproto.wlr_virtual_pointer_unstable_v1 import ZwlrVirtualPointerManagerV1  # noqa: E402

BTN_LEFT = 0x110
extent_w, extent_h = int(sys.argv[2]), int(sys.argv[3])

display = Display()
display.connect()
registry = display.get_registry()
found = {}


def on_global(registry, name, interface, version):
    if interface == "wl_seat" and "seat" not in found:
        found["seat"] = registry.bind(name, WlSeat, 1)
    elif interface == ZwlrVirtualPointerManagerV1.name:
        found["manager"] = registry.bind(name, ZwlrVirtualPointerManagerV1, 1)


registry.dispatcher["global"] = on_global
display.roundtrip()
pointer = found["manager"].create_virtual_pointer(found["seat"])
display.roundtrip()


def now():
    return int(time.monotonic() * 1000) & 0xFFFFFFFF


for line in sys.stdin:
    command, *args = line.split()
    if command == "move":
        pointer.motion_absolute(now(), int(args[0]), int(args[1]), extent_w, extent_h)
    elif command == "press":
        pointer.button(now(), BTN_LEFT, 1)
    elif command == "release":
        pointer.button(now(), BTN_LEFT, 0)
    pointer.frame()
    display.flush()
    print("ok", flush=True)

pointer.destroy()
display.flush()
# Leave before Python's teardown frees proxies that outlive the connection, which crashes pywayland.
os._exit(0)
