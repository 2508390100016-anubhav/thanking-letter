#!/usr/bin/env python3
"""ASCII love-letter animation for the terminal.   python letter.py [Name]
Make the terminal big (or full screen) and press Ctrl+C to quit."""
import colorsys, math, os, random, shutil, sys, time

NAME = " ".join(sys.argv[1:]) or "You"
MSG = [f"Hey {NAME},", "this little letter is just for you.",
       "You make ordinary days special.", "Glad you are in my life <3"]
RAMP = " .:-=+*#%@"
ASP = 0.5                      # terminal cell width / height
os.system("")                  # enables ANSI colours on Windows

def rgb(h, s, v):
    r, g, b = colorsys.hsv_to_rgb((h % 360) / 360, s, clamp(v))
    return f"\x1b[38;2;{int(r*255)};{int(g*255)};{int(b*255)}m"

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): return x * x * (3 - 2 * x)

class Screen:
    def __init__(self):
        self.cols, self.rows = shutil.get_terminal_size()
        self.rows -= 1
        self.cells = {}
    def put(self, x, y, ch, col):
        x, y = int(x), int(y)
        if 0 <= x < self.cols and 0 <= y < self.rows:
            self.cells[(x, y)] = (ch, col)
    def line(self, x0, y0, x1, y1, ch, col):
        n = int(max(abs(x1 - x0), abs(y1 - y0))) or 1
        for i in range(n + 1):
            self.put(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n, ch, col)
    def center(self, s, y, col, n=None):
        x0 = (self.cols - len(s)) // 2
        for i, ch in enumerate(s[:len(s) if n is None else max(0, n)]):
            self.put(x0 + i, y, ch, col)
    def render(self):
        out = ["\x1b[H"]
        for y in range(self.rows):
            last = None
            for x in range(self.cols):
                ch, col = self.cells.get((x, y), (" ", None))
                if ch != " " and col != last:
                    out.append(col); last = col
                out.append(ch)
            out.append("\x1b[0m\n")
        sys.stdout.write("".join(out)); sys.stdout.flush()

def main():
    parts, next_burst = [], 0.0
    t0 = last = time.time()
    sys.stdout.write("\x1b[2J\x1b[?25l")
    try:
        while True:
            now = time.time(); dt = min(0.05, now - last); last = now
            T = now - t0 - 1.5                       # envelope opens by itself after 1.5 s
            s = Screen(); cols, rows = s.cols, s.rows
            ew = min(cols - 4, 40); eh = max(6, int(ew * 0.42))
            ex = (cols - ew) // 2; ey = max(8, rows - eh - 7); cx = cols / 2
            R = max(3, min(ey / 2.3, 10))
            cream, dim = rgb(25, .3, 1), rgb(15, .5, .55)

            hp = ease(clamp((T - 1.2) / 2.2))        # heart rising out of the envelope
            if hp > 0:
                cy_f = ey - R - 1
                cy = ey + eh / 2 + (cy_f - ey - eh / 2) * hp
                r = R * (.3 + .7 * hp) * (1 + .05 * math.sin(now * 6.5))
                for j in range(max(0, int(cy - r * 1.1)), min(ey, int(cy + r * 1.1) + 1)):
                    for i in range(int(cx - r * 2 / ASP * .5), int(cx + r * 2 / ASP * .5) + 1):
                        u = (i - cx) * ASP / r * 1.3; v = (cy - j) / r * 1.3
                        f = (u*u + v*v - 1) ** 3 - u*u * v**3
                        if f <= 0:
                            d = clamp(-f * 2.5)
                            s.put(i, j, RAMP[2 + int(d * 7.99)], rgb(350 + d * 10, .85, .6 + .4 * d))

            for y in range(eh + 1):                   # envelope body
                for x in range(ew):
                    edge = y in (0, eh) or x in (0, ew - 1)
                    s.put(ex + x, ey + y, "#" if edge else ("." if (x + y) % 4 == 0 else " "),
                          cream if edge else dim)
            s.line(ex, ey + eh, cx, ey + eh * .55, "/", dim)
            s.line(ex + ew - 1, ey + eh, cx, ey + eh * .55, "\\", dim)
            o = 0 if T < 0 else ease(clamp(T / 1.4))  # flap
            tip = ey + eh * .55 * math.cos(o * math.pi)
            down, up = tip > ey + 1, tip < ey - 1
            s.line(ex, ey, cx, tip, "\\" if down else "/" if up else "-", cream)
            s.line(ex + ew - 1, ey, cx, tip, "/" if down else "\\" if up else "-", cream)

            if T > 3 and now > next_burst:            # fireworks
                next_burst = now + .9
                bx, by = cols * random.uniform(.2, .8), rows * random.uniform(.1, .4)
                h = random.uniform(0, 360)
                for _ in range(46):
                    a, sp = random.uniform(0, 6.283), random.uniform(4, 13)
                    parts.append([bx, by, math.cos(a) * sp * 1.9, math.sin(a) * sp, 1.0, h])
            parts = [p for p in parts if p[4] > 0]
            for p in parts:
                p[3] += 9 * dt; p[2] *= .985; p[0] += p[2] * dt; p[1] += p[3] * dt; p[4] -= dt * .55
                s.put(p[0], p[1], RAMP[max(1, int(p[4] * 9))], rgb(p[5], 1, .5 + .5 * p[4]))

            if T < 0:
                s.center("A  L E T T E R  F O R  Y O U", 2, cream)
            elif T > 3.2:
                n = int((T - 3.2) * 24)
                for i, line in enumerate(MSG):
                    s.center(line, ey + eh + 2 + i, rgb(345, .6, 1) if i == 3 else cream, n)
                    n -= len(line)
            s.render()
            time.sleep(max(0, 1 / 30 - (time.time() - now)))
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write("\x1b[0m\x1b[?25h\x1b[2J\x1b[H")

if __name__ == "__main__":
    main()
