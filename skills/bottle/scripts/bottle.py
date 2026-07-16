#!/usr/bin/env python3
"""终端漂流瓶客户端 — 基于 gh CLI 与公共海域仓库交互。

用法:
  bottle.py throw <正文>     扔一只漂流瓶
  bottle.py fish             捞一只漂流瓶（同时检查自己瓶子的新回音）
  bottle.py reply <回音>     给刚捞到的瓶子留回音
"""
import hashlib
import json
import random
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from render_bottle import calm, fished_art, sealed  # noqa: E402

REPO = "xixicc186/drift-bottle-sea"
STATE_FILE = Path.home() / ".bottle" / "state.json"
META_RE = re.compile(r"<!--\s*bottle-meta\s*(\{.*?\})\s*-->", re.S)

PREFIXES = ["咸鱼", "逐浪", "守塔", "拾贝", "候鸟", "锚链", "雾航", "潮汐",
            "远帆", "礁石", "海雾", "星槎", "浮木", "环礁", "深潜", "灯船"]
ROLES = ["水手", "船长", "灯塔员", "潜水员", "舵手", "渔夫", "瞭望员", "旅人"]


def gh(*args, input_=None):
    r = subprocess.run(["gh", *args], capture_output=True, text=True, input=input_)
    if r.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args[:3])} 失败: {r.stderr.strip()}")
    return r.stdout


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(state):
    STATE_FILE.parent.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2))


def identity():
    login = gh("api", "user", "-q", ".login").strip()
    h = hashlib.sha256(login.encode()).hexdigest()[:16]
    n = int(h[:8], 16)
    codename = f"{PREFIXES[n % 16]}{ROLES[(n >> 4) % 8]} #{n % 10000:04d}"
    return login, h, codename


def parse_meta(body):
    m = META_RE.search(body or "")
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None


def bottle_text(body):
    return META_RE.sub("", body or "").strip()


def cmd_throw(content):
    content = content.strip()
    n = len(content)
    if n < 10:
        sys.exit("⚖️ 瓶子太轻了（正文不足 10 字），会浮不起来。多写几句吧。")
    if n > 500:
        sys.exit("⚖️ 瓶子太重了（正文超过 500 字），会沉底。精简一下吧。")
    _, h, codename = identity()
    meta = {"author_hash": h,
            "thrown_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "v": 1}
    body = f"<!-- bottle-meta {json.dumps(meta)} -->\n\n{content}"
    url = gh("issue", "create", "-R", REPO,
             "--title", f"🍾 {codename} 的漂流瓶",
             "--body-file", "-", input_=body).strip()
    print(sealed(codename))
    print(f"\n（过审后入海 · {url}）")


def check_echoes(state, my_hash):
    """查自己被捞走的瓶子有没有新回音。"""
    last_check = state.get("last_echo_check", "1970-01-01T00:00:00Z")
    out = gh("issue", "list", "-R", REPO, "--author", "@me", "--state", "all",
             "--label", "caught", "--limit", "50",
             "--json", "number,title,body,comments")
    echoes = []
    for issue in json.loads(out):
        meta = parse_meta(issue["body"])
        if not meta or meta.get("author_hash") != my_hash:
            continue
        for c in issue.get("comments", []):
            if c["body"].startswith("🌊 回音") and c["createdAt"] > last_check:
                echoes.append((issue["number"], bottle_text(issue["body"]), c["body"]))
    state["last_echo_check"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return echoes


def cmd_fish():
    _, my_hash, codename = identity()
    state = load_state()

    for num, original, echo in check_echoes(state, my_hash):
        print(f"📬 你扔出的瓶子（#{num}「{original[:20]}…」）收到了回音：")
        print(f"   {echo}\n")

    out = gh("issue", "list", "-R", REPO, "--label", "floating", "--state", "open",
             "--limit", "100", "--json", "number,title,body")
    pool = []
    for issue in json.loads(out):
        meta = parse_meta(issue["body"])
        if meta and meta.get("author_hash") != my_hash:
            pool.append(issue)

    random.shuffle(pool)
    for issue in pool:
        num = issue["number"]
        # 抢占式认领：先确认仍在漂，改标后再 close；失败说明被别人抢了，换下一只
        try:
            cur = json.loads(gh("issue", "view", str(num), "-R", REPO,
                                "--json", "labels,state"))
            if cur["state"] != "OPEN" or not any(
                    l["name"] == "floating" for l in cur["labels"]):
                continue
            gh("issue", "edit", str(num), "-R", REPO,
               "--add-label", "caught", "--remove-label", "floating")
            gh("issue", "close", str(num), "-R", REPO,
               "--comment", f"🎣 这只瓶子被 {codename} 捞走了。")
        except RuntimeError:
            continue
        meta = parse_meta(issue["body"])
        state["last_caught"] = num
        save_state(state)
        print("🎣 捞到一只瓶子！\n")
        print(fished_art(bottle_text(issue["body"]),
                     sender=sailor_name(meta["author_hash"]),
                     date=floated(meta.get("thrown_at"))))
        print("\n（想回应的话：/bottle reply <你的回音>）")
        return

    save_state(state)
    print(calm())
    print("\n（要不你先扔一只？/bottle throw）")


def floated(thrown_at):
    """瓶子漂了多久，人话表述。"""
    try:
        dt = datetime.strptime(thrown_at, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return ""
    secs = (datetime.now(timezone.utc) - dt).total_seconds()
    if secs < 3600:
        return "不到一小时"
    if secs < 86400:
        return f"{int(secs // 3600)} 小时"
    return f"{int(secs // 86400)} 天"


def sailor_name(author_hash):
    n = int(author_hash[:8], 16)
    return f"{PREFIXES[n % 16]}{ROLES[(n >> 4) % 8]} #{n % 10000:04d}"


def cmd_reply(text):
    text = text.strip()
    if not text:
        sys.exit("回音不能是空的。")
    state = load_state()
    num = state.get("last_caught")
    if not num:
        sys.exit("你手里还没有捞到的瓶子，先 /bottle fish 一只吧。")
    _, _, codename = identity()
    gh("issue", "comment", str(num), "-R", REPO,
       "--body", f"🌊 回音 · 来自 {codename}：{text}")
    print(f"🌊 回音已放进瓶子 #{num}，扔回海里了。瓶子主人下次出海会收到。")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd, rest = sys.argv[1], " ".join(sys.argv[2:])
    if cmd == "throw":
        cmd_throw(rest)
    elif cmd == "fish":
        cmd_fish()
    elif cmd == "reply":
        cmd_reply(rest)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
