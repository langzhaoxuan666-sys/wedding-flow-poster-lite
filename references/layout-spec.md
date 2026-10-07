# Wedding Flow Poster Lite — Layout Spec v1.1

## Canvas and layering
- Canvas: 1080 × 1920 px, 9:16.
- Center axis: X = 540 px.
- Background and typography are separate layers.
- Render order: background layer → transparent HTML/CSS text PNG → pixel-level alpha composite → final PNG.
- Never ask an image-generation model to draw or rewrite text.

## Hard top-to-bottom order
The renderer owns the order. Agents must never hand-author alternate HTML/CSS.

When fields exist, the only valid vertical order is:
1. couple names;
2. date;
3. optional event label (for example 婚礼晚宴, only when supplied by the user);
4. venue;
5. 50×2 divider;
6. start time;
7. 婚礼流程;
8. 50×2 divider;
9. wedding flow items in confirmed order;
10. optional AFTER PARTY title;
11. 50×2 divider;
12. after-party items in confirmed order.

If an optional field is absent, omit it without moving later blocks above earlier blocks. Never use `column-reverse`, CSS `order`, bottom anchoring, or any layout mechanism that can reverse visual order.

## Text bounding box target
Reference target:
- X ≈ 346.5 → 733.5 px;
- Y ≈ 252 → 1687 px;
- visible text height ≈ 1435 px ≈ 74.7% canvas height;
- top whitespace ≈ 13.1%;
- bottom whitespace ≈ 12.1%.

Use a 620 px logical safe region (≈57.4% canvas width), but do not stretch text to fill it. Typical actual longest text should stay around 36%–40% of canvas width.

## Type scale
Reference body size is 28 px.
- couple names: 53 px ≈ body × 1.9;
- main section title: 33 px ≈ body × 1.18;
- AFTER PARTY: 31 px ≈ body × 1.11;
- metadata, start time, flow body: 28 px.

If the whole composition exceeds the bottom safety line, scale the complete typography system proportionally. Do not shrink only the body text while leaving headings oversized.

## Line rhythm
- Chinese body top-to-top step: ~50 px ≈ 28 × 1.79.
- After Party top-to-top step: ~52 px ≈ 28 × 1.86.
- When font size changes, line rhythm and section spacing scale with it.
- Never increase font size without proportional spacing.

## Module rhythm
- Couple names → basic info: strong pause, about 46–58 px.
- Date / event label / venue: one grouped information block, about 50 px row rhythm.
- Venue → divider → start time: compact information module.
- Start time → 婚礼流程: strong section break.
- Wedding flow → AFTER PARTY: at least one full body line step of extra module spacing.

## Dividers
- 50 × 2 px.
- Center aligned.
- Accent color only.
- Visual punctuation, never a long region separator.

## Color
- primary: `#3B3029`;
- accent: `#9B4C2E`.

Accent may be used for:
- the `&` in couple names;
- 婚礼流程;
- AFTER PARTY;
- short dividers.

All ordinary body text stays primary. Default text-color count: 2.

## Font
Preferred stack:
`"Noto Serif CJK SC", "Source Han Serif SC", "Songti SC", "STSong", serif`.

- couple names and 婚礼流程: 700;
- body and AFTER PARTY: 400 unless a platform font requires a minor fallback adjustment.

## Content constraints
- Every visible flow item is one concise event label.
- Prefer 2–10 Chinese characters, maximum 16.
- Keep confirmed order exactly.
- No backstage notes, staff reminders, parenthetical instructions, props handling, or semicolon-separated sub-actions.
