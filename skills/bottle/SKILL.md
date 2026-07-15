---
name: bottle
description: >
  终端漂流瓶。把一句话装进瓶子扔进公共的海（GitHub 仓库），或从海里随机捞一只
  陌生人的瓶子，还能给捞到的瓶子留回音。当用户说"扔/丢个漂流瓶"、"捞个瓶子"、
  "捞一下漂流瓶"、"看看海里有什么"、"回个瓶子"、"drift bottle"、"/bottle" 等
  任何漂流瓶相关操作时使用。前提：gh CLI 已登录。
---

# 终端漂流瓶

公共海域仓库：`xixicc186/drift-bottle-sea`（issue = 瓶子，Actions 审核后打
`floating` 标签才可被捞）。客户端脚本：`scripts/bottle.py`（依赖 gh CLI）。

## 子命令

### throw — 扔瓶子

1. **先做内容软审核**（这一步由你判断，不靠脚本）：正文若包含手机号、住址、
   邮箱等隐私信息，或人身攻击、广告引流、违法内容，礼貌拒绝并说明原因，
   建议用户改写。健康的情绪抒发、提问、碎碎念、祝福都欢迎。
2. 正文需 10~500 字。不足或超出时提醒用户增删，不要擅自改写用户的话。
3. 过审后执行：
   ```bash
   python3 ~/.claude/skills/bottle/scripts/bottle.py throw "<正文>"
   ```
4. 告诉用户瓶子已入海、正在等审核（仓库 Actions 过审后才漂进渔场）。

### fish — 捞瓶子

```bash
python3 ~/.claude/skills/bottle/scripts/bottle.py fish
```

- 脚本会先报告用户自己的瓶子有没有收到新回音，再随机捞一只别人的瓶子。
- 把瓶中信内容用有仪式感的方式展示给用户（可以配简短的 ASCII 小瓶子），
  并提醒可以用 reply 回音。
- 如果海是空的（捞到海草），顺势鼓励用户扔一只。

### reply — 回音

```bash
python3 ~/.claude/skills/bottle/scripts/bottle.py reply "<回音>"
```

- 回音针对最近一次捞到的瓶子。同样先做一遍内容软审核（同 throw 标准）。
- 没捞过瓶子时脚本会提示先去 fish。

## 注意

- 用户没说清楚子命令时，根据语义判断：想倾诉/发出去的 → throw；想看看
  别人的/随机来一个 → fish；针对刚捞到的瓶子说话 → reply。
- 脚本报 gh 相关错误时，先让用户确认 `gh auth status`。
- 不要绕过脚本直接操作 issue，认领逻辑（防止两人捞到同一只）在脚本里。
