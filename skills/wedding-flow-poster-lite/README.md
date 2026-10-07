# Wedding Flow Poster Lite

把杂乱的婚礼资料交给 AI：**先清洗成简洁流程 → 你确认 → 再生成海报**。

## 两步完成

1. AI 只整理海报需要的内容：新人、日期、时间、地点、简洁流程；
2. 确认后调用固定 renderer，用真实 HTML/CSS 文字 + 暖白纸张背景生成 1080×1920 PNG。

不会把伴郎递麦、督导提醒、服装、音乐、来宾人数、准备物品等执行信息塞进海报。

## v1.1 排版锁定

本版修复跨环境排版不一致问题：Chat / Work 都不得自行写一套 HTML。确认后必须调用 bundled renderer。

固定从上到下：

```text
新人姓名
日期 / 可选婚礼类型 / 地点
短分隔线
开始时间
婚礼流程
短分隔线
流程正文
可选 AFTER PARTY
```

禁止反向排列，禁止 `column-reverse`、CSS `order`、底部锚定。

排版基准：正文 28px；新人姓名 53px；婚礼流程 33px；AFTER PARTY 31px；正文步进约 50px；文字区顶部约 13%，底部约 12%。详见 `references/layout-spec.md`。

## 本地渲染

```bash
python scripts/render_poster.py examples/confirmed.json output.png \
  --text-layer text.png \
  --background-layer background.png
```

需要 Python Playwright + Chromium 与 Pillow。

## License

MIT
