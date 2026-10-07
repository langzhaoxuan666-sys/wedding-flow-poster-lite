---
name: wedding-flow-poster-lite
description: Use when a user provides messy wedding workflow notes, voice-transcribed ceremony text, or an execution rundown and wants a clean wedding flow poster.
---

# Wedding Flow Poster Lite

## Overview
Turn messy wedding notes into a **poster-ready flow**, then render it only after the user confirms it. The core rule is:

**clean to poster content → confirm → render**

This Skill is not a wedding brief, execution sheet, meeting summary, or planning document.

## Stage 1 — Produce a poster-ready clean draft
Read only the user-provided text/files. Extract only information that can actually appear on the Lite poster:

- couple names;
- wedding date;
- start time;
- venue;
- ordered flow item names.

Clean fillers, duplicate wording, obvious speech-to-text noise, punctuation, and overly long phrases. Preserve facts and order. Do not invent missing steps or times.

### Content-clarity rules
The first response must be **short, visual, and poster-oriented**, not exhaustive.

For flow items:
- one event per line;
- target 2–10 Chinese characters; keep under 16 characters whenever possible;
- use a concise event label such as `新郎入场`, `新人告白`, `交换戒指`, `父母登场`;
- remove backstage/execution details from the poster draft: who passes microphones, who opens doors, who reminds, who retrieves props, stage positions, clothing, music, guest counts, atmosphere notes, preparation lists, story copy, staffing, and similar production notes;
- do not put semicolon-separated sub-actions, multiple clauses, or long parenthetical notes into one flow item;
- if a detail does not change the visible event name, silently omit it from the Lite draft;
- if wording is genuinely ambiguous **and changes what the visible event should be called**, use the safest generic label or mark only that item for confirmation. Do not turn every source note into a clarification question.

Do **not** create extra sections such as `来宾信息`, `婚礼想法`, `音乐`, `开场白方向`, `婚礼需要准备`, `伴郎伴娘分工`, or `执行备注`.

### Required Stage-1 response shape
Use this compact structure:

```text
新人：测试新郎 & 测试新娘
日期：2026.10.18
时间：11:08
地点：示例酒店

婚礼流程
1. 主持人开场
2. 新郎入场
3. 新娘入场
4. 新人告白
5. 交换戒指
6. 父母登场
7. 父亲致辞
8. 合影

请确认以上文字、信息和顺序是否正确。需要修改直接告诉我；确认无误后告诉我“生成海报”。
```

Omit unknown optional metadata instead of inventing it.

Show the **complete cleaned poster draft** and wait. Do not render before explicit confirmation, even if the first message says “直接生成”. If the user changes anything, show the full updated poster draft again and wait for confirmation again.

Treat replies such as “确认”, “没问题”, “就这样”, “可以生成”, or equivalent as confirmation only when they refer to the latest cleaned draft.

## Stage 2 — Render only the confirmed draft
After confirmation, create JSON matching:

```json
{
  "coupleNames": "测试新郎 & 测试新娘",
  "date": "2026.10.18",
  "venue": "示例酒店",
  "startTime": "11:08",
  "title": "婚礼流程",
  "items": ["主持人开场", "新郎入场", "新娘入场"]
}
```

`items` must contain only the confirmed concise event labels, in confirmed order. Never reinsert execution notes removed during Stage 1.

Render with:

```bash
python scripts/render_poster.py confirmed.json output.png
```

If Playwright is unavailable, use an available Chromium/Chrome browser renderer for the same HTML/CSS. Never replace real text with ImageGen.

## Fixed visual rules
- Canvas: 1080×1920, 9:16.
- Fixed bundled warm-white paper texture only.
- Real HTML/CSS text.
- Centered, minimal layout; no timeline, cards, people, logo, or watermark.
- Primary text `#302D29`; accent `#9B4C2E` only for the small divider.
- Maximum two text colors by default.
- Couple names are largest but restrained; metadata is smaller/lighter.
- Flow size/gap may reduce only as needed to avoid overflow.

## Output
Return the PNG as an accessible attachment/link. Do not expose a temporary path as the only delivery method.

## Never do
- Never turn the source into a comprehensive wedding brief.
- Never render execution instructions inside flow items.
- Never invent missing facts, steps, or times.
- Never skip the confirmation gate.
- Never offer background/font/theme choices in Lite.
- Never use production Poster Workspace services, secrets, or customer data.
