#!/usr/bin/env python3
import math
import shutil
import sys
import time
import numpy as np

def render(cols, rows, t):
    width = min(cols, 120)
    height = max(20, (rows - 1) * 2)
    aspect = height / width

    x = np.linspace(-1.0, 1.0, width)
    y = np.linspace(-1.0, 1.0, height) * aspect
    X, Y = np.meshgrid(x, y)

    radius = np.sqrt(X ** 2 + Y ** 2) + 1e-6
    angle = np.arctan2(Y, X)

    horizon = 0.16 * (1.0 + 0.18 * math.sin(t * 1.3))
    photon_ring = horizon * 1.5

    with np.errstate(divide="ignore", invalid="ignore"):
        source_radius = radius * np.sqrt(
            np.clip(1.0 - (horizon / radius) ** 1.4, 0.0, None)
        )

    twist = 2.2 * np.exp(
        -((radius - photon_ring) ** 2) / (2.0 * 0.12 ** 2)
    )
    bent_angle = angle + twist * math.sin(t * 0.6)

    pattern = np.sin(source_radius * 26.0)
    pattern *= np.sin(bent_angle * 10.0 + t * 0.4)

    glow = np.exp(
        -((radius - photon_ring) ** 2) / (2.0 * 0.025 ** 2)
    )

    brightness = np.clip(
        (0.5 + 0.5 * pattern) * 0.65 + glow * 1.6,
        0.0,
        1.0,
    )
    brightness[radius <= horizon] = 0.0

    red = np.clip(brightness ** 1.4 * 255, 0, 255).astype(np.uint8)
    green = np.clip(brightness ** 1.1 * 190, 0, 255).astype(np.uint8)
    blue = np.clip((0.15 + brightness * 0.75) * 255, 0, 255).astype(np.uint8)

    return red, green, blue, width, height // 2

def draw(red, green, blue, width, rows):
    output = []

    for row in range(rows):
        top = row * 2
        bottom = top + 1
        line = []

        for col in range(width):
            tr, tg, tb = red[top, col], green[top, col], blue[top, col]
            br, bg, bb = red[bottom, col], green[bottom, col], blue[bottom, col]

            line.append(
                f"\x1b[38;2;{tr};{tg};{tb}m"
                f"\x1b[48;2;{br};{bg};{bb}m\u2580"
            )

        line.append("\x1b[0m")
        output.append("".join(line))

    sys.stdout.write("\x1b[H" + "\n".join(output))
    sys.stdout.flush()

def main():
    t = 0.0
    sys.stdout.write("\x1b[2J\x1b[H\x1b[?25l")

    try:
        while True:
            size = shutil.get_terminal_size(fallback=(80, 40))
            red, green, blue, width, rows = render(
                size.columns,
                size.lines,
                t,
            )
            draw(red, green, blue, width, rows)
            t += 0.08
            time.sleep(0.04)

    except KeyboardInterrupt:
        pass

    finally:
        sys.stdout.write("\x1b[0m\x1b[?25h\nStopped.\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
