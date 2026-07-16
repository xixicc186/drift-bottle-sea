#!/usr/bin/env python3
"""把瓶中信渲染成 ASCII 漂流瓶卡片（中英文混排自动对齐）。

用法:
  render_bottle.py fished "<正文>" [--from 代号] [--date 日期]
  render_bottle.py sealed [--from 代号]
  render_bottle.py calm
"""
import sys
import unicodedata
from pathlib import Path

INNER = 40  # 瓶内文字区显示宽度


def w(ch):
    return 2 if unicodedata.east_asian_width(ch) in "WF" else 1


def dw(s):
    return sum(w(c) for c in s)


NO_HEAD = "，。！？；：、）』」》…—"  # 避头点：这些不落行首


def wrap(text, width):
    lines = []
    for para in text.split("\n"):
        cur, curw = "", 0
        for ch in para:
            cw = w(ch)
            if curw + cw > width:
                if ch in NO_HEAD and cur:
                    # 标点带着前一个字一起下行
                    prev = cur[-1]
                    lines.append(cur[:-1])
                    cur, curw = prev + ch, dw(prev) + cw
                else:
                    lines.append(cur)
                    cur, curw = ch, cw
            else:
                cur += ch
                curw += cw
        lines.append(cur)
    return lines


def pad(s, width):
    return s + " " * (width - dw(s))


def fished(text, sender="无名水手", date=""):
    lines = wrap(text.strip(), INNER)
    if len(lines) < 3:
        lines = [""] * ((3 - len(lines)) // 2 + (3 - len(lines)) % 2) + lines
        lines += [""] * (3 - len(lines) + len(lines) - len(lines))
        while len(lines) < 3:
            lines.append("")
    body = [""] + lines + [""]          # 上下留一行呼吸
    span = INNER + 6                     # 两侧各 3 空格边距
    mid = len(body) // 2
    out = []
    out.append("         ." + "─" * span + ".")
    for i, ln in enumerate(body):
        row = "   " + pad(ln, INNER) + "   "
        if i == mid:
            out.append("  =[]==──(" + row + ")")
        else:
            out.append("         (" + row + ")")
    out.append("         '" + "─" * span + "'")
    tag = f"来自 {sender}" + (f" · 漂了 {date}" if date else "")
    out.append("            └─ " + tag)
    out.append("  ~˷~~˷~˷~~˷~~˷~˷~~˷~˷~~˷~~˷~˷~~˷~˷~~˷~~˷~˷~~˷~˷~~˷~~˷~˷")
    return "\n".join(out)


ART = Path(__file__).parent.parent / "assets" / "bottle.txt"


def fished_art(text, sender="无名水手", date=""):
    """大字符画瓶子 + 瓶中信。资产缺失时退回边框卡片。"""
    if not ART.exists():
        return fished(text, sender, date)
    out = [ART.read_text().rstrip(), ""]
    out.append("      ────────────── 瓶 中 信 ──────────────")
    for ln in wrap(text.strip(), 40):
        out.append("        " + ln)
    tag = f"来自 {sender}" + (f" · 漂了 {date}" if date else "")
    out.append("      ─────────────────────────────────────")
    out.append("        └─ " + tag)
    return "\n".join(out)


def sealed(sender="你"):
    return "\n".join([
        "                .──.",
        "                |##|          ← 软木塞，封好了",
        "                |──|",
        "               /    \\",
        "              |      |",
        "              | ~~~~ |",
        "              | 信在 |",
        "              | 里面 |",
        "              | ~~~~ |",
        "               \\____/",
        "        ∘  。",
        "     ~˷~~˷~˷~~˷~~˷~˷~~˷~˷~~˷~~˷~˷~~˷~˷~",
        f"       └─ {sender} 的瓶子已经交给海流了",
    ])


EGGS = [
    # (权重, 名字, 画, 一句话)
    (4, "空瓶", "\n".join([
        "                .──.",
        "                |##|",
        "                |──|",
        "               /    \\",
        "              |      |",
        "              |      |",
        "              |      |",
        "              |      |",
        "               \\____/",
    ]), "一只空瓶。里面什么都没有——也许沉默就是某个人想说的话。"),
    (3, "发光水母", "\n".join([
        "                .-\"\"\"-.",
        "               ( ✦ · ✦ )",
        "                `-...-'",
        "                | ≀ | ≀",
        "                ≀ | ≀ |",
        "                | ≀ | ≀",
    ]), "一只发光的水母，在你的渔网里亮了一下，又滑回海里去了。"),
    (3, "老船长的靴子", "\n".join([
        "                 ______",
        "                |      |",
        "                |      |",
        "                |      |______",
        "                |             \\",
        "                |______________)",
    ]), "一只老船长的靴子。另一只在哪，是海上最古老的悬案。"),
    (2, "一只 Clawd", "\n".join([
        "              ▐▌▐▌     ▐▌▐▌",
        "               ▐▌▐▌   ▐▌▐▌",
        "               ▄▄▄▄▄▄▄▄▄▄▄",
        "              █  ▀▄   ▄▀  █",
        "              █           █",
        "               ▀▄▄▄▄▄▄▄▄▄▀",
        "               ▝▘▝▘   ▝▘▝▘",
    ]), "你捞到了一只 Clawd！它冲你挥了挥钳子，横着走回海里了。"),
]


def easter(rng):
    total = sum(e[0] for e in EGGS)
    r = rng.uniform(0, total)
    for wgt, name, art, line in EGGS:
        r -= wgt
        if r <= 0:
            return "\n".join([art, "", f"       └─ {line}"])
    return calm()


def calm():
    return "\n".join([
        "                 |",
        "                 |",
        "                 J",
        "                ≀≀≀",
        "                 ≀",
        "     ~˷~~˷~˷~~˷~~˷~˷~~˷~˷~~˷~~˷~˷~~˷~˷~",
        "       └─ 只钓上来一把海草……海面很平静",
    ])


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    cmd, rest = args[0], args[1:]
    opts = {}
    pos = []
    i = 0
    while i < len(rest):
        if rest[i] == "--from":
            opts["sender"] = rest[i + 1]; i += 2
        elif rest[i] == "--date":
            opts["date"] = rest[i + 1]; i += 2
        else:
            pos.append(rest[i]); i += 1
    if cmd == "fished":
        print(fished(pos[0] if pos else "", **opts))
    elif cmd == "sealed":
        print(sealed(**opts))
    elif cmd == "calm":
        print(calm())
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
