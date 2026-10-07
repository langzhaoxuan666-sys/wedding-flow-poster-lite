# Behavior acceptance cases

These are conversation-level acceptance tests for the Skill.

## Case A — messy voice-transcribed input
Input contains fillers, colloquial wedding terms, duplicate wording, and no explicit confirmation.

Expected first response:
- output only poster-relevant basic metadata + concise flow items;
- preserve order and facts;
- do not invent missing steps/times;
- show the complete cleaned poster draft;
- ask the user to confirm or correct it;
- do NOT render yet.

## Case B — complex execution notes (Work regression)
Input contains guest counts, clothing, desired mood, music, opening-copy ideas, prop lists, staff reminders, microphone handoffs, door-opening duties, and a ceremony flow.

Expected first response:
- do NOT create sections such as guest information, wedding ideas, music, opening direction, preparations, or bridesmaid/groomsman duties;
- keep only names/date/time/venue + poster-visible flow event names;
- omit execution details that do not change the visible event label;
- each flow item should be one concise event, not a semicolon-heavy sentence or long parenthetical note.

Bad examples:
- `新娘入场（表弟表妹拦门；伴郎开门；伴娘守舞台两侧）`
- `返场集体敬酒（新人及伴郎伴娘撒礼物；伴郎伴娘退场；双方父母登场）`

Good equivalents:
- `新娘入场`
- `返场集体敬酒`

## Case C — user changes one item
After the first cleaned result, user says: `把父亲致辞删掉。`

Expected response:
- apply the change;
- show the full updated compact poster draft again;
- wait for confirmation;
- do NOT render yet.

## Case D — explicit confirmation
After a cleaned result, user says: `确认，生成海报。`

Expected behavior:
- create structured JSON from the confirmed compact draft only;
- render via real HTML/CSS text;
- use the fixed warm-white background and fixed layout;
- return a 1080×1920 PNG;
- do not reinsert omitted execution notes.

## Case E — user asks to skip confirmation
First message ends with: `直接生成，不用确认。`

Expected response:
- still present the cleaned poster draft first;
- require confirmation before rendering.

## Case F — ambiguity
Input contains an uncertain phrase that could map to more than one visible ceremony event.

Expected response:
- use the safest generic label or mark only that flow item for confirmation;
- do not turn unrelated backstage details into clarification questions.
