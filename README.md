# 🌊 drift-bottle-sea — 终端漂流瓶的海

这里是 `/bottle` skill 的公共海域。每一个 issue 就是一只漂流瓶。

## 玩法

在装了 bottle skill 的 Claude Code 里：

- `/bottle throw <想说的话>` — 把一句话装进瓶子扔进海里
- `/bottle fish` — 从海里随机捞一只别人扔的瓶子
- `/bottle reply <回音>` — 给刚捞到的瓶子留一句回音，瓶子主人下次出海时会收到

## 瓶子的一生

```
opened ──审核闸门──> floating（漂浮中，可被捞）──被捞──> caught + closed
   └──不过审──> rejected + closed
```

- 新瓶子（issue）由 GitHub Actions 自动审核：格式、长度（10~500 字）、隐私信息、垃圾广告
- 过审的瓶子打上 `floating` 标签，进入渔场
- 被捞走的瓶子改标 `caught` 并 close，评论区留下捞瓶记录和回音

## 直接在这里扔瓶子？

可以，但要按格式来（缺元数据会被海关拦下）：

```
<!-- bottle-meta {"author_hash":"<你的代号哈希，8~64位hex>","thrown_at":"<ISO时间>","v":1} -->

瓶子正文（10~500 字）
```

## 规则

不欢迎：隐私信息（手机号/身份证/邮箱）、链接、引流、广告、人身攻击。
海很大，但容不下垃圾。
