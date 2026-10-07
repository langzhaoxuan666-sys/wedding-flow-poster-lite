# Fixed layout specification

- Canvas: 1080 × 1920 px, 9:16.
- Background: bundled fixed warm-white paper asset (`assets/warm-white-paper.svg`).
- Paper base tone: warm ivory around `#F8F5EE`; texture is intentionally subtle and low-contrast.
- Primary text: `#302D29`.
- Accent: `#9B4C2E`, used only for the small divider/accent.
- Maximum two text colors by default.
- Center axis, generous whitespace, no timeline or card UI.
- Couple names: serif, about 58 px reference size, medium/semi-bold rather than extra-heavy.
- Metadata: about 21 px, visually subordinate to the names.
- Section title: about 31 px.
- Flow text adapts roughly from 34 px (short) to 25 px (long), then may reduce further only to prevent overflow.
- Every flow item is one poster-visible event label, ideally 2–10 Chinese characters and no more than 16 characters.
- Do not render parentheses, semicolon-separated sub-actions, staff reminders, prop handling, or other execution notes in flow items.
- Flow items keep the user-confirmed order exactly.
- The poster must use real HTML/CSS text. Never rasterize text with an image generator.
