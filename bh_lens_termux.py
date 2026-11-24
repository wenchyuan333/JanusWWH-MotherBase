#!/usr/bin/env python3
import math
import shutil
import sys
import time
import numpy as np
def get_term_size():
size = shutil.get_terminal_size(fallback=(80, 40))
return size.columns, size.lines
def render_frame(cols, rows, t):
width = cols
height = rows * 2
aspect = height / width
xs = np.linspace(-1.0, 1.0, width)
ys = np.linspace(-1.0, 1.0, height) * aspect
x_grid, y_grid = np.meshgrid(xs, ys)
radius = np.sqrt(x_grid ** 2 + y_grid ** 2) + 1e-6
theta = np.arctan2(y_grid, x_grid)
schwarzschild_radius = 0.16 * (1.0 + 0.35 * math.sin(t * 1.3))
photon_radius = 1.5 * schwarzschild_radius
with np.errstate(divide="ignore", invalid="ignore"):
source_radius = radius * np.sqrt(
np.clip(
1.0 - (schwarzschild_radius / radius) ** 1.4,
0.0,
None,
)
)
inside_horizon = radius <= schwarzschild_radius
twist = 2.2 * np.exp(
-((radius - photon_radius) ** 2) / (2.0 * 0.12 ** 2)
)
bent_theta = theta + twist * math.sin(t * 0.6)
checker = np.sin(source_radius * 26.0)
checker = checker * np.sin(bent_theta * 10.0 + t * 0.4)
ring_glow = np.exp(
-((radius - photon_radius) ** 2) / (2.0 * 0.02 ** 2)
)
brightness = 0.5 + 0.5 * checker
brightness = brightness * 0.75 + ring_glow * 1.4
brightness = np.clip(brightness, 0.0, 1.0)
brightness[inside_horizon] = 0.0
red = np.clip(brightness ** 1.6 * 255, 0, 255)
green = np.clip(brightness ** 1.1 * 200, 0, 255)
blue = np.clip((0.35 + brightness * 0.65) * 255, 0, 255)
return (
red.astype(np.uint8),
green.astype(np.uint8),
blue.astype(np.uint8),
)
def draw(red, green, blue, rows, cols):
output = []
for row in range(rows):
top = row * 2
bottom = top + 1
parts = []
for col in range(cols):
top_red = red[top, col]
top_green = green[top, col]
top_blue = blue[top, col]
bottom_red = red[bottom, col]
bottom_green = green[bottom, col]
bottom_blue = blue[bottom, col]
color = (
f"\x1b[38;2;{top_red};{top_green};{top_blue}m"
f"\x1b[48;2;{bottom_red};{bottom_green};{bottom_blue}m"
"\u2580"
)
parts.append(color)
parts.append("\x1b[0m")
output.append("".join(parts))
sys.stdout.write("\x1b[H")
sys.stdout.write("\n".join(output))
sys.stdout.flush()
def main():
animation_time = 0.0
sys.stdout.write("\x1b[2J\x1b[H\x1b[?25l")
sys.stdout.flush()
try:
while True:
cols, rows = get_term_size()
rows = max(10, rows - 1)
red, green, blue = render_frame(
cols,
rows,
animation_time,
)
draw(red, green, blue, rows, cols)
animation_time += 0.08
time.sleep(0.04)
except KeyboardInterrupt:
pass
finally:
sys.stdout.write("\x1b[0m\x1b[?25h\nStopped.\n")
sys.stdout.flush()
if name == "main":
main()
