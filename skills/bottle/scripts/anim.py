#!/usr/bin/env python3
"""漂流瓶终端动画 — ANSI 逐帧重绘。

用法: anim.py [throw|fish|calm|all]
非 tty 环境下只打印最终帧（避免控制码刷屏）。
"""
import math
import sys
import time

W, H = 58, 11
SURF = 6  # 水面所在行

RESET = "\033[0m"
def C(n): return f"\033[38;5;{n}m"

STAR = C(245); MOON = C(230)
WATER = [C(51), C(45), C(39), C(38), C(32)]
BOTTLE = C(222); CORK = C(180); LINE = C(255)
SPARK = C(229); FOAM = C(195); GREEN = C(71)


def new_grid():
    return [[" "] * W for _ in range(H)], [[""] * W for _ in range(H)]


def put(g, x, y, s, color=""):
    ch, co = g
    x, y = int(round(x)), int(round(y))
    for i, c in enumerate(s):
        if 0 <= x + i < W and 0 <= y < H and c != " ":
            ch[y][x + i] = c
            co[y][x + i] = color


def base(t, g):
    for sx, sy in ((5, 1), (15, 0), (27, 2), (38, 1), (52, 0), (45, 2)):
        if (t // 4 + sx) % 5:
            put(g, sx, sy, ".", STAR)
    put(g, 49, 1, "☾", MOON)
    pat = "~~≈~-~≈~~~"
    for r in range(SURF, H):
        d = r - SURF
        col = WATER[min(d, len(WATER) - 1)]
        speed = 1 if d % 2 == 0 else -1
        row = "".join(pat[(x + speed * t + d * 3) % len(pat)] for x in range(W))
        put(g, 0, r, row, col)


def render(g):
    ch, co = g
    lines = []
    for y in range(H):
        s, cur = "", None
        for x in range(W):
            col = co[y][x]
            if col != cur:
                s += RESET + col
                cur = col
            s += ch[y][x]
        lines.append(s + RESET)
    return lines


def play(nframes, build, msg="", fps=13):
    out = sys.stdout
    if not out.isatty():
        g = new_grid()
        build(nframes - 1, g)
        print("\n".join(render(g)))
        if msg:
            print(msg)
        return
    out.write("\033[?25l")
    try:
        for t in range(nframes):
            g = new_grid()
            build(t, g)
            if t:
                out.write(f"\033[{H}A")
            out.write("\n".join("\033[2K" + l for l in render(g)) + "\n")
            out.flush()
            time.sleep(1 / fps)
    except KeyboardInterrupt:
        pass
    finally:
        out.write("\033[?25h")
        out.flush()
    if msg:
        print(msg)


def draw_bottle(g, x, y):
    """y 为瓶身所在行，瓶塞在上一行。"""
    put(g, x + 1, y - 1, "!", CORK)
    put(g, x, y, "[:]", BOTTLE)


# ── 场景一：扔瓶 ──────────────────────────────────────────────

def throw(t, g):
    base(t, g)
    FLY, LX = 15, 42
    if t < FLY:                       # 抛物线飞行
        p = t / FLY
        x = 2 + p * (LX - 2)
        y = (SURF - 1) - 4.2 * math.sin(math.pi * p)
        put(g, x, y, "/-\\|"[t % 4], BOTTLE)
    elif t < FLY + 4:                 # 入水水花
        k = t - FLY
        if k == 0:
            put(g, LX, SURF, "*", FOAM)
        elif k == 1:
            put(g, LX - 1, SURF - 1, "o o", FOAM)
        elif k == 2:
            put(g, LX - 2, SURF - 1, "∘   ∘", FOAM)
            put(g, LX, SURF, "O", FOAM)
        else:
            put(g, LX - 1, SURF, ": :", FOAM)
    else:                             # 漂浮远去
        x = LX + (t - FLY - 4) * 0.45
        bob = (t // 4) % 2
        draw_bottle(g, x, SURF - bob)


# ── 场景二：捞瓶 ──────────────────────────────────────────────

def fish(t, g):
    base(t, g)
    DROP, CX = 10, 30
    if t < DROP:                      # 垂线下降
        yh = 1 + t * (SURF - 1) / DROP
        for y in range(0, int(yh)):
            put(g, CX, y, "|", LINE)
        put(g, CX, yh, "J", LINE)
    elif t < 18:                      # 等待，水面涟漪
        for y in range(0, SURF):
            put(g, CX, y, "|", LINE)
        r = (t - DROP) % 3 + 1
        put(g, CX - r, SURF, "(", FOAM)
        put(g, CX + r, SURF, ")", FOAM)
    elif t < 20:                      # 咬钩抖动
        jig = 1 if t % 2 else -1
        for y in range(0, SURF):
            put(g, CX + (jig if y % 2 else 0), y, "|", LINE)
        put(g, CX + 2, SURF - 1, "!", SPARK)
    else:                             # 收线，瓶子出水
        p = min((t - 20) / 8, 1.0)
        by = SURF - int(3 * p)        # 瓶身行 6 → 3
        for y in range(0, by - 1):
            put(g, CX, y, "|", LINE)
        draw_bottle(g, CX - 1, by)
        if by > 3:
            put(g, CX - 1, by + 1, "' '", WATER[1])
        if p >= 1 and t % 3:          # 出水后闪光
            pts = ((-4, 0), (5, -1), (-3, -2), (6, 1))
            sx, sy = pts[t % 4]
            put(g, CX + sx, by + sy, "✦·*"[t % 3], SPARK)


# ── 场景三：海草（空军） ──────────────────────────────────────

def calm(t, g):
    base(t, g)
    DROP, CX = 8, 30
    if t < DROP:
        yh = 1 + t * (SURF - 1) / DROP
        for y in range(0, int(yh)):
            put(g, CX, y, "|", LINE)
        put(g, CX, yh, "J", LINE)
    elif t < 16:
        for y in range(0, SURF):
            put(g, CX, y, "|", LINE)
    else:
        p = min((t - 16) / 8, 1.0)
        hy = SURF - int(3 * p)        # 钩子行 6 → 3
        sway = 1 if (t // 3) % 2 else 0
        for y in range(0, hy):
            put(g, CX, y, "|", LINE)
        put(g, CX, hy, "J", LINE)
        put(g, CX - 1 + sway, hy + 1, "≀≀", GREEN)
        put(g, CX + sway, hy + 2, "≀", GREEN)


SCENES = {
    "throw": (46, throw, "🍾 瓶子漂进了深海，等一个有缘人。"),
    "fish": (44, fish, "🎣 有货！一只瓶子上钩了。"),
    "calm": (36, calm, "🌫️ 只捞到一把海草……海面很平静。"),
}


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd == "all":
        for i, (n, fn, msg) in enumerate(SCENES.values()):
            play(n, fn, msg)
            if i < len(SCENES) - 1:
                time.sleep(0.8)
                if sys.stdout.isatty():
                    sys.stdout.write(f"\033[{H + 1}A")
    elif cmd in SCENES:
        play(*SCENES[cmd])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
