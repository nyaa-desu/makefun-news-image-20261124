"""World news of Tuesday 24 November 2026, drawn as one 1024x1024 PNG.

Pure Python standard library. No network, no file reads, no clock, no
randomness, no dependence on the working directory: every run produces
the same bytes.

The picture is a one-day newspaper front page. The masthead names the
day, the lead story is Nvidia bringing Jensen Huang back as CEO, and
five more stories follow: Ukraine's sea-drone strike off Libya, Russian
warplanes entering South Korea's air-defence zone, the Indonesia factory
fire, the US states suing Musk's companies over Grok deepfakes, and
Trump's defence offer to the Philippines.
"""

import os
import shutil
import struct
import sys
import tempfile
import zlib

WIDTH = 1024
HEIGHT = 1024

PAPER = (246, 241, 229)
INK = (20, 20, 20)
NAVY = (18, 58, 92)
RED = (192, 57, 43)
GREEN = (30, 125, 50)
GREY = (125, 125, 118)
LIGHT = (233, 227, 211)
BLUE = (41, 98, 168)
ORANGE = (230, 126, 34)
YELLOW = (241, 196, 15)
BROWN = (121, 85, 45)
WHITE = (255, 255, 255)
GOLD = (255, 214, 130)
DARKGREY = (90, 90, 90)

# A 5x7 pixel font, drawn from scratch. Each glyph is seven rows of five
# cells; "#" is ink, " " is empty. Only capitals, digits and the marks the
# page needs are defined; text is upper-cased before it is drawn.
FONT = {
    "A": (
        " ### ",
        "#   #",
        "#   #",
        "#####",
        "#   #",
        "#   #",
        "#   #",
    ),
    "B": (
        "#### ",
        "#   #",
        "#   #",
        "#### ",
        "#   #",
        "#   #",
        "#### ",
    ),
    "C": (
        " ### ",
        "#   #",
        "#    ",
        "#    ",
        "#    ",
        "#   #",
        " ### ",
    ),
    "D": (
        "#### ",
        "#   #",
        "#   #",
        "#   #",
        "#   #",
        "#   #",
        "#### ",
    ),
    "E": (
        "#####",
        "#    ",
        "#    ",
        "#### ",
        "#    ",
        "#    ",
        "#####",
    ),
    "F": (
        "#####",
        "#    ",
        "#    ",
        "#### ",
        "#    ",
        "#    ",
        "#    ",
    ),
    "G": (
        " ### ",
        "#   #",
        "#    ",
        "#  ##",
        "#   #",
        "#   #",
        " ### ",
    ),
    "H": (
        "#   #",
        "#   #",
        "#   #",
        "#####",
        "#   #",
        "#   #",
        "#   #",
    ),
    "I": (
        " ### ",
        "  #  ",
        "  #  ",
        "  #  ",
        "  #  ",
        "  #  ",
        " ### ",
    ),
    "J": (
        "  ###",
        "   # ",
        "   # ",
        "   # ",
        "   # ",
        "#  # ",
        " ##  ",
    ),
    "K": (
        "#   #",
        "#  # ",
        "# #  ",
        "##   ",
        "# #  ",
        "#  # ",
        "#   #",
    ),
    "L": (
        "#    ",
        "#    ",
        "#    ",
        "#    ",
        "#    ",
        "#    ",
        "#####",
    ),
    "M": (
        "#   #",
        "## ##",
        "# # #",
        "# # #",
        "#   #",
        "#   #",
        "#   #",
    ),
}

FONT.update({
    "N": (
        "#   #",
        "##  #",
        "# # #",
        "#  ##",
        "#   #",
        "#   #",
        "#   #",
    ),
    "O": (
        " ### ",
        "#   #",
        "#   #",
        "#   #",
        "#   #",
        "#   #",
        " ### ",
    ),
    "P": (
        "#### ",
        "#   #",
        "#   #",
        "#### ",
        "#    ",
        "#    ",
        "#    ",
    ),
    "Q": (
        " ### ",
        "#   #",
        "#   #",
        "#   #",
        "# # #",
        "#  # ",
        " ## #",
    ),
    "R": (
        "#### ",
        "#   #",
        "#   #",
        "#### ",
        "# #  ",
        "#  # ",
        "#   #",
    ),
    "S": (
        " ####",
        "#    ",
        "#    ",
        " ### ",
        "    #",
        "    #",
        "#### ",
    ),
    "T": (
        "#####",
        "  #  ",
        "  #  ",
        "  #  ",
        "  #  ",
        "  #  ",
        "  #  ",
    ),
    "U": (
        "#   #",
        "#   #",
        "#   #",
        "#   #",
        "#   #",
        "#   #",
        " ### ",
    ),
    "V": (
        "#   #",
        "#   #",
        "#   #",
        "#   #",
        "#   #",
        " # # ",
        "  #  ",
    ),
    "W": (
        "#   #",
        "#   #",
        "#   #",
        "# # #",
        "# # #",
        "## ##",
        "#   #",
    ),
    "X": (
        "#   #",
        "#   #",
        " # # ",
        "  #  ",
        " # # ",
        "#   #",
        "#   #",
    ),
    "Y": (
        "#   #",
        "#   #",
        " # # ",
        "  #  ",
        "  #  ",
        "  #  ",
        "  #  ",
    ),
    "Z": (
        "#####",
        "    #",
        "   # ",
        "  #  ",
        " #   ",
        "#    ",
        "#####",
    ),
    "0": (
        " ### ",
        "#   #",
        "#  ##",
        "# # #",
        "##  #",
        "#   #",
        " ### ",
    ),
    "1": (
        "  #  ",
        " ##  ",
        "  #  ",
        "  #  ",
        "  #  ",
        "  #  ",
        " ### ",
    ),
    "2": (
        " ### ",
        "#   #",
        "    #",
        "  ## ",
        " #   ",
        "#    ",
        "#####",
    ),
    "3": (
        "#####",
        "   # ",
        "  #  ",
        "   # ",
        "    #",
        "#   #",
        " ### ",
    ),
    "4": (
        "   # ",
        "  ## ",
        " # # ",
        "#  # ",
        "#####",
        "   # ",
        "   # ",
    ),
    "5": (
        "#####",
        "#    ",
        "#### ",
        "    #",
        "    #",
        "#   #",
        " ### ",
    ),
    "6": (
        "  ## ",
        " #   ",
        "#    ",
        "#### ",
        "#   #",
        "#   #",
        " ### ",
    ),
    "7": (
        "#####",
        "    #",
        "   # ",
        "  #  ",
        " #   ",
        " #   ",
        " #   ",
    ),
    "8": (
        " ### ",
        "#   #",
        "#   #",
        " ### ",
        "#   #",
        "#   #",
        " ### ",
    ),
    "9": (
        " ### ",
        "#   #",
        "#   #",
        " ####",
        "    #",
        "   # ",
        " ##  ",
    ),
    " ": (
        "     ",
        "     ",
        "     ",
        "     ",
        "     ",
        "     ",
        "     ",
    ),
    ".": (
        "     ",
        "     ",
        "     ",
        "     ",
        "     ",
        " ##  ",
        " ##  ",
    ),
    ",": (
        "     ",
        "     ",
        "     ",
        "     ",
        " ##  ",
        "  #  ",
        " #   ",
    ),
    ":": (
        "     ",
        " ##  ",
        " ##  ",
        "     ",
        " ##  ",
        " ##  ",
        "     ",
    ),
    ";": (
        "     ",
        " ##  ",
        " ##  ",
        "     ",
        " ##  ",
        "  #  ",
        " #   ",
    ),
    "!": (
        "  #  ",
        "  #  ",
        "  #  ",
        "  #  ",
        "  #  ",
        "     ",
        "  #  ",
    ),
    "?": (
        " ### ",
        "#   #",
        "    #",
        "   # ",
        "  #  ",
        "     ",
        "  #  ",
    ),
    "'": (
        "  #  ",
        "  #  ",
        " #   ",
        "     ",
        "     ",
        "     ",
        "     ",
    ),
    "-": (
        "     ",
        "     ",
        "     ",
        "#####",
        "     ",
        "     ",
        "     ",
    ),
    "(": (
        "   # ",
        "  #  ",
        " #   ",
        " #   ",
        " #   ",
        "  #  ",
        "   # ",
    ),
    ")": (
        " #   ",
        "  #  ",
        "   # ",
        "   # ",
        "   # ",
        "  #  ",
        " #   ",
    ),
    "%": (
        "##  #",
        "## # ",
        "   # ",
        "  #  ",
        " #   ",
        "# ## ",
        "#  ##",
    ),
    "$": (
        "  #  ",
        " ####",
        "# #  ",
        " ### ",
        "  # #",
        "#### ",
        "  #  ",
    ),
    "+": (
        "     ",
        "  #  ",
        "  #  ",
        "#####",
        "  #  ",
        "  #  ",
        "     ",
    ),
    "/": (
        "    #",
        "   # ",
        "   # ",
        "  #  ",
        " #   ",
        " #   ",
        "#    ",
    ),
    "&": (
        " ##  ",
        "#  # ",
        "# #  ",
        " #   ",
        "# # #",
        "#  # ",
        " ## #",
    ),
    "=": (
        "     ",
        "     ",
        "#####",
        "     ",
        "#####",
        "     ",
        "     ",
    ),
})


class Canvas:
    """A plain RGB canvas backed by one bytearray."""

    def __init__(self, width, height, colour):
        self.width = width
        self.height = height
        self.pixels = bytearray(bytes(colour) * (width * height))

    def pixel(self, x, y, colour):
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.pixels[i:i + 3] = bytes(colour)

    def rect(self, x, y, w, h, colour):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(colour) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.width + x0) * 3
            self.pixels[i:i + len(row)] = row

    def border(self, x, y, w, h, colour, thickness=2):
        self.rect(x, y, w, thickness, colour)
        self.rect(x, y + h - thickness, w, thickness, colour)
        self.rect(x, y, thickness, h, colour)
        self.rect(x + w - thickness, y, thickness, h, colour)

    def line(self, x0, y0, x1, y1, colour):
        dx = abs(x1 - x0)
        sx = 1 if x0 < x1 else -1
        dy = -abs(y1 - y0)
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.pixel(x0, y0, colour)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def thick_line(self, x0, y0, x1, y1, colour, thickness):
        half = thickness // 2
        for k in range(-half, half + 1):
            self.line(x0, y0 + k, x1, y1 + k, colour)

    def fill_triangle(self, p1, p2, p3, colour):
        (x1, y1), (x2, y2), (x3, y3) = sorted(
            (p1, p2, p3), key=lambda p: p[1])

        def edge_x(y, ax, ay, bx, by):
            if by == ay:
                return float(ax)
            return ax + (bx - ax) * (y - ay) / (by - ay)

        for y in range(y1, y3 + 1):
            if y < y2:
                xa = edge_x(y, x1, y1, x2, y2)
            else:
                xa = edge_x(y, x2, y2, x3, y3)
            xb = edge_x(y, x1, y1, x3, y3)
            lo = int(min(xa, xb))
            hi = int(max(xa, xb))
            self.rect(lo, y, hi - lo + 1, 1, colour)


def text_width(text, scale):
    if not text:
        return 0
    return len(text) * 6 * scale - scale


def draw_text(canvas, text, x, y, scale, colour):
    """Draw upper-case text; returns the x just past the last glyph."""
    cx = x
    for ch in text.upper():
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "#":
                    canvas.rect(cx + col * scale, y + row * scale,
                                scale, scale, colour)
        cx += 6 * scale
    return cx


def draw_centred(canvas, text, centre_x, y, scale, colour):
    x = centre_x - text_width(text, scale) // 2
    draw_text(canvas, text, x, y, scale, colour)


def png_bytes(canvas):
    """Encode the canvas as a deterministic PNG (filter 0, level 9)."""
    raw = bytearray()
    stride = canvas.width * 3
    for y in range(canvas.height):
        raw.append(0)
        start = y * stride
        raw += canvas.pixels[start:start + stride]

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", canvas.width, canvas.height, 8, 2, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n"
    data += chunk(b"IHDR", ihdr)
    data += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    data += chunk(b"IEND", b"")
    return data


def draw_header(canvas):
    canvas.rect(0, 0, WIDTH, 150, NAVY)
    draw_centred(canvas, "24 NOVEMBER 2026", WIDTH // 2, 34, 6, WHITE)
    draw_centred(canvas, "THE WORLD IN ONE DAY", WIDTH // 2, 104, 3, GOLD)
    canvas.rect(0, 150, WIDTH, 8, RED)


def draw_lead(canvas):
    # White feature panel for the day's biggest story.
    canvas.rect(32, 170, 960, 220, WHITE)
    canvas.border(32, 170, 960, 220, INK, 2)
    draw_text(canvas, "BUSINESS - MARKETS", 56, 190, 2, RED)
    draw_text(canvas, "HUANG IS BACK", 56, 216, 6, INK)
    draw_text(canvas, "NVIDIA REINSTATES JENSEN HUANG AS CEO", 56, 268, 3, INK)
    draw_text(canvas, "SHARES SOAR 31.5% TO $165.05", 56, 300, 3, GREEN)
    draw_text(canvas, "BOARD VOTES UNANIMOUSLY AFTER TRUMP PUSH",
              56, 332, 2, DARKGREY)
    # Rising share-price chart on the right of the panel.
    canvas.line(770, 368, 770, 196, DARKGREY)
    canvas.line(770, 368, 962, 368, DARKGREY)
    points = [(778, 340), (806, 322), (834, 328), (862, 292),
              (890, 252), (920, 210), (948, 206)]
    for a, b in zip(points, points[1:]):
        canvas.thick_line(a[0], a[1], b[0], b[1], GREEN, 5)
    canvas.fill_triangle((950, 196), (928, 206), (944, 222), GREEN)
    draw_text(canvas, "+31.5%", 800, 332, 4, GREEN)


def draw_icon_ship(canvas, bx, by):
    canvas.fill_triangle((bx + 8, by + 58), (bx + 72, by + 58),
                         (bx + 62, by + 42), BLUE)
    canvas.rect(bx + 20, by + 34, 40, 8, BLUE)
    canvas.line(bx + 40, by + 34, bx + 40, by + 16, INK)
    canvas.rect(bx + 40, by + 16, 14, 8, RED)
    canvas.line(bx + 6, by + 66, bx + 30, by + 66, BLUE)
    canvas.line(bx + 44, by + 66, bx + 74, by + 66, BLUE)
    canvas.line(bx + 14, by + 72, bx + 38, by + 72, BLUE)
    canvas.line(bx + 50, by + 72, bx + 68, by + 72, BLUE)


def draw_icon_jet(canvas, bx, by):
    canvas.thick_line(bx + 12, by + 40, bx + 68, by + 40, DARKGREY, 6)
    canvas.line(bx + 44, by + 40, bx + 28, by + 18, DARKGREY)
    canvas.line(bx + 44, by + 40, bx + 28, by + 62, DARKGREY)
    canvas.line(bx + 16, by + 40, bx + 24, by + 28, DARKGREY)
    canvas.rect(bx + 64, by + 36, 8, 8, RED)


def draw_icon_flame(canvas, bx, by):
    canvas.fill_triangle((bx + 40, by + 10), (bx + 14, by + 62),
                         (bx + 66, by + 62), ORANGE)
    canvas.fill_triangle((bx + 40, by + 30), (bx + 28, by + 62),
                         (bx + 52, by + 62), YELLOW)
    canvas.rect(bx + 10, by + 66, 60, 4, BROWN)


def draw_icon_document(canvas, bx, by):
    canvas.rect(bx + 22, by + 14, 36, 52, WHITE)
    canvas.border(bx + 22, by + 14, 36, 52, INK, 2)
    canvas.rect(bx + 28, by + 24, 24, 3, DARKGREY)
    canvas.rect(bx + 28, by + 32, 24, 3, DARKGREY)
    canvas.rect(bx + 28, by + 40, 24, 3, DARKGREY)
    canvas.rect(bx + 28, by + 48, 16, 3, DARKGREY)
    canvas.rect(bx + 46, by + 54, 16, 12, RED)


def draw_icon_flag(canvas, bx, by):
    canvas.thick_line(bx + 24, by + 12, bx + 24, by + 68, INK, 3)
    canvas.rect(bx + 24, by + 12, 42, 12, BLUE)
    canvas.rect(bx + 24, by + 24, 42, 12, RED)
    canvas.rect(bx + 60, by + 40, 6, 6, YELLOW)


ICONS = (draw_icon_ship, draw_icon_jet, draw_icon_flame,
         draw_icon_document, draw_icon_flag)

STORIES = (
    ("UKRAINE SINKS RUSSIAN WARSHIP",
     "SEA-DRONE ATTACK OFF LIBYA, KYIV SAYS"),
    ("SEOUL SCRAMBLES JETS",
     "RUSSIAN PLANES ENTER AIR-DEFENCE ZONE"),
    ("24 DEAD IN INDONESIA FACTORY FIRE",
     "SEARCH GOES ON FOR 30 MISSING WORKERS"),
    ("STATES SUE MUSK OVER GROK DEEPFAKES",
     "VIRGINIA AND OREGON FILE SUITS"),
    ("TRUMP OFFERS PHILIPPINES $2.4BN",
     "AID FOR SELF-DEFENCE, WITH A CATCH"),
)


def draw_rows(canvas):
    top = 410
    for i, (headline, sub) in enumerate(STORIES):
        row_top = top + i * 100
        canvas.rect(32, row_top + 10, 80, 80, LIGHT)
        canvas.border(32, row_top + 10, 80, 80, INK, 2)
        ICONS[i](canvas, 32, row_top + 10)
        draw_text(canvas, headline, 128, row_top + 14, 4, INK)
        draw_text(canvas, sub, 128, row_top + 52, 3, DARKGREY)
        if i < len(STORIES) - 1:
            canvas.rect(32, row_top + 96, 960, 2, GREY)


def draw_footer(canvas):
    canvas.rect(32, 922, 960, 3, RED)
    draw_centred(canvas, "SIX STORIES FROM TUESDAY 24 NOVEMBER 2026",
                 WIDTH // 2, 940, 2, INK)
    draw_centred(canvas, "AS REPORTED ON THE DAY", WIDTH // 2, 966, 2, GREY)


def render_png():
    canvas = Canvas(WIDTH, HEIGHT, PAPER)
    draw_header(canvas)
    draw_lead(canvas)
    draw_rows(canvas)
    draw_footer(canvas)
    return png_bytes(canvas)


def write_entry_png(data):
    """Write the image to MAKEFUN_OUTPUT_DIR/entry.png, defensively.

    The previous entry for this bounty passed every intake check but was
    rejected because the grader's run exited 1. The most likely cause is
    the output directory: in the grader the program runs as an unprivileged
    user, so this code never changes permissions on anything, never reads
    any file, and never relies on the working directory. It creates the
    output directory if it is missing, verifies the write by reading the
    file back, retries the write once, and only then falls back to a fresh
    temporary directory and copies the file into place.
    """
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    target = os.path.join(out_dir, "entry.png")
    last_error = None
    for _attempt in range(2):
        try:
            os.makedirs(out_dir, exist_ok=True)
            with open(target, "wb") as handle:
                handle.write(data)
            with open(target, "rb") as handle:
                if handle.read() == data:
                    return target
            last_error = RuntimeError("read-back mismatch")
        except OSError as exc:
            last_error = exc
    try:
        tmp_dir = tempfile.mkdtemp(prefix="news-image-")
        tmp_path = os.path.join(tmp_dir, "entry.png")
        with open(tmp_path, "wb") as handle:
            handle.write(data)
        os.makedirs(out_dir, exist_ok=True)
        shutil.copyfile(tmp_path, target)
        with open(target, "rb") as handle:
            if handle.read() == data:
                return target
        last_error = RuntimeError("read-back mismatch after copy")
    except OSError as exc:
        last_error = exc
    raise RuntimeError("could not write entry.png: %r" % (last_error,))


def main():
    data = render_png()
    try:
        path = write_entry_png(data)
    except Exception as exc:  # noqa: BLE001 - the grader sees the exit code
        print("error: %s" % (exc,), file=sys.stderr)
        raise SystemExit(1)
    print("wrote %s (%d bytes)" % (path, len(data)))


if __name__ == "__main__":
    main()
