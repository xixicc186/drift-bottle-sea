#!/usr/bin/env python3
"""把图片转成字符画。

用法: asciify.py <图片> [--width 96] [--color] [--out 文件]
--color 输出 24-bit ANSI 真彩色（终端 cat 用）；不加则输出纯文本（markdown 代码块用）。
"""
import argparse
import sys

from PIL import Image

# 由疏到密的字符梯度（暗 → 亮）
RAMP = " .`'^:;!i|/(1fjtxnvczmwqpdbkhao*#%8&@$"


def asciify(path, width, color):
    img = Image.open(path).convert("RGB")
    w0, h0 = img.size
    # 终端字符高约为宽的 2.1 倍
    height = max(1, round(h0 / w0 * width / 2.1))
    img = img.resize((width, height), Image.LANCZOS)
    lines = []
    for y in range(height):
        row = []
        prev = None
        for x in range(width):
            r, g, b = img.getpixel((x, y))
            lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
            ch = RAMP[min(int(lum / 256 * len(RAMP)), len(RAMP) - 1)]
            if color and ch != " ":
                # 提亮一点，终端黑底上更接近原图观感
                rr, gg, bb = (min(255, int(c * 1.15)) for c in (r, g, b))
                code = f"\033[38;2;{rr};{gg};{bb}m"
                row.append((code if code != prev else "") + ch)
                prev = code
            else:
                row.append(ch)
                if ch == " ":
                    prev = None
        line = "".join(row).rstrip()
        lines.append(line + ("\033[0m" if color and line else ""))
    # 去掉上下全空行
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--width", type=int, default=96)
    ap.add_argument("--color", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args()
    art = asciify(a.image, a.width, a.color)
    if a.out:
        with open(a.out, "w") as f:
            f.write(art + "\n")
        print(f"written: {a.out}", file=sys.stderr)
    else:
        print(art)


if __name__ == "__main__":
    main()
