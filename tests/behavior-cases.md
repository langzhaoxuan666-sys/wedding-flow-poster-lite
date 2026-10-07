# Behavior acceptance cases

## Case A — messy voice-transcribed input
Expected first response: only poster-relevant metadata + concise ordered flow, then confirmation. No rendering yet.

## Case B — complex execution notes
Guest counts, clothing, mood, music, prop lists, staff reminders and microphone handoffs must not appear in the Lite poster draft.

Bad: `新娘入场（伴郎开门；伴娘舞台两侧）`  
Good: `新娘入场`

Bad: `返场集体敬酒（新人及伴郎伴娘撒礼物；双方父母登场）`  
Good: `返场集体敬酒`

## Case C — revision before confirmation
If the user changes one item, show the whole updated compact draft and wait again.

## Case D — renderer ownership / Work regression
After confirmation, the agent must serialize JSON and call `scripts/render_poster.py`. It must not create its own alternative HTML/CSS poster.

Required visual order is always top-to-bottom: names → info → divider → start time → 婚礼流程 → divider → flow → optional AFTER PARTY.

Failure examples:
- `婚礼流程` appears below the last flow item;
- names or headline appear at the bottom;
- flow items are visually reversed;
- CSS contains `column-reverse`, custom `order`, or bottom anchoring.

## Case E — explicit confirmation
Only after confirmation: render separate background and transparent text layers, then composite to final PNG.

## Case F — first-message “直接生成”
Still require the cleaned draft confirmation first.
