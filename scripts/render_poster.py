#!/usr/bin/env python3
import argparse
import base64
import html
import json
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PAPER_ASSET = ROOT / 'assets' / 'warm-white-paper.svg'
CANVAS_W = 1080
CANVAS_H = 1920
TOP_Y = 252
TARGET_BOTTOM_Y = 1687
TARGET_TEXT_HEIGHT = TARGET_BOTTOM_Y - TOP_Y
MIN_SCALE = 0.82
MAX_FLOW_ITEM_CHARS = 16
MAX_FLOW_ITEMS = 24
FORBIDDEN_FLOW_PUNCTUATION = set('，,；;：:（）()【】[]\n\r')


def esc(value):
    return html.escape(str(value or ''), quote=True)


def paper_data_uri():
    if not PAPER_ASSET.exists():
        raise FileNotFoundError(f'fixed background asset missing: {PAPER_ASSET}')
    encoded = base64.b64encode(PAPER_ASSET.read_bytes()).decode('ascii')
    return f'data:image/svg+xml;base64,{encoded}'


def validate_items(items, field='items'):
    cleaned = [str(x).strip() for x in (items or []) if str(x).strip()]
    if field == 'items' and not cleaned:
        raise ValueError('items must contain at least one flow item')
    if len(cleaned) > MAX_FLOW_ITEMS:
        raise ValueError(f'{field} has {len(cleaned)} items; Lite supports at most {MAX_FLOW_ITEMS} visible flow items on one poster')
    for index, item in enumerate(cleaned, start=1):
        if len(item) > MAX_FLOW_ITEM_CHARS:
            raise ValueError(
                f'{field} item {index} is too verbose for Lite poster ({len(item)} chars): {item!r}. '
                f'Use one concise visible event label, preferably 2-10 Chinese characters and at most {MAX_FLOW_ITEM_CHARS} characters.'
            )
        if any(ch in FORBIDDEN_FLOW_PUNCTUATION for ch in item):
            raise ValueError(
                f'{field} item {index} contains execution-note punctuation: {item!r}. '
                'Remove parenthetical notes, semicolon-separated sub-actions, staff reminders, and backstage details before rendering.'
            )
    return cleaned


def validate_poster_data(data):
    items = validate_items(data.get('items'), 'items')
    after_party_items = validate_items(data.get('afterPartyItems'), 'afterPartyItems') if data.get('afterPartyItems') else []
    if len(items) + len(after_party_items) > MAX_FLOW_ITEMS:
        raise ValueError(f'combined visible items exceed Lite limit of {MAX_FLOW_ITEMS}')
    return items, after_party_items


def render_names(value):
    text = esc(value or '')
    if not text:
        return ''
    # The ampersand is the only accent inside the couple-name line.
    text = text.replace('&amp;', '<span class="name-accent">&amp;</span>')
    return text


def build_text_html(data):
    items, after_party_items = validate_poster_data(data)

    names = render_names(data.get('coupleNames'))
    date = esc(data.get('date') or '')
    event_label = esc(data.get('eventLabel') or '')
    venue = esc(data.get('venue') or '')
    start_time = esc(data.get('startTime') or '')
    title = esc(data.get('title') or '婚礼流程')
    after_title = esc(data.get('afterPartyTitle') or 'AFTER PARTY')

    item_html = ''.join(f'<div class="flow-item">{esc(item)}</div>' for item in items)
    after_html = ''.join(f'<div class="after-item">{esc(item)}</div>' for item in after_party_items)

    info_rows = ''.join(
        f'<div class="info-line">{value}</div>'
        for value in [date, event_label, venue]
        if value
    )

    after_party_block = ''
    if after_party_items:
        after_party_block = f'''
        <section class="after-party" data-block="after-party">
          <div class="after-title">{after_title}</div>
          <div class="divider divider-c"></div>
          <div class="after-list">{after_html}</div>
        </section>'''

    return f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<style>
:root {{
  --text-primary: #3B3029;
  --accent: #9B4C2E;
  --body-size: 28px;
  --body-step: 50px;
  --after-step: 52px;
  --layout-scale: 1;
}}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; width: {CANVAS_W}px; height: {CANVAS_H}px; overflow: hidden; background: transparent !important; }}
body {{
  color: var(--text-primary);
  font-family: "Noto Serif CJK SC", "Source Han Serif SC", "Songti SC", "STSong", serif;
  -webkit-font-smoothing: antialiased;
  text-rendering: geometricPrecision;
}}
.poster-text {{
  position: absolute;
  top: {TOP_Y}px;
  left: 50%;
  width: 620px;
  max-width: 57.4%;
  margin: 0;
  padding: 0;
  transform: translateX(-50%) scale(var(--layout-scale));
  transform-origin: top center;
  text-align: center;
}}
.names {{
  margin: 0;
  font-size: 53px;
  font-weight: 700;
  line-height: 1.12;
  letter-spacing: .025em;
  white-space: nowrap;
}}
.name-accent {{ color: var(--accent); }}
.info {{
  margin-top: 46px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}}
.info-line,
.start-time,
.flow-item,
.after-item {{
  font-size: var(--body-size);
  font-weight: 400;
  line-height: 1.42;
  letter-spacing: .025em;
}}
.divider {{
  width: 50px;
  height: 2px;
  margin-left: auto;
  margin-right: auto;
  background: var(--accent);
  flex: 0 0 auto;
}}
.divider-a {{ margin-top: 12px; }}
.start-time {{ margin-top: 38px; }}
.main-title {{
  margin-top: 58px;
  color: var(--accent);
  font-size: 33px;
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: .06em;
}}
.divider-b {{ margin-top: 20px; }}
.flow {{
  margin-top: 38px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: calc(var(--body-step) - (var(--body-size) * 1.42));
}}
.flow-item {{ max-width: 620px; }}
.after-party {{ margin-top: 50px; }}
.after-title {{
  color: var(--accent);
  font-size: 31px;
  font-weight: 400;
  line-height: 1.2;
  letter-spacing: .06em;
}}
.divider-c {{ margin-top: 14px; }}
.after-list {{
  margin-top: 38px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: calc(var(--after-step) - (var(--body-size) * 1.42));
}}
.after-item {{ max-width: 620px; }}
</style>
</head>
<body>
<main class="poster-text" data-block="poster-text">
  {f'<h1 class="names" data-block="names">{names}</h1>' if names else ''}
  {f'<section class="info" data-block="info">{info_rows}</section>' if info_rows else ''}
  <div class="divider divider-a" data-block="divider-a"></div>
  {f'<div class="start-time" data-block="start-time">开始时间 | {start_time}</div>' if start_time else ''}
  <div class="main-title" data-block="main-title">{title}</div>
  <div class="divider divider-b" data-block="divider-b"></div>
  <section class="flow" data-block="flow">{item_html}</section>
  {after_party_block}
</main>
<script>
(async function lockLayout() {{
  if (document.fonts && document.fonts.ready) await document.fonts.ready;
  const root = document.documentElement;
  const content = document.querySelector('.poster-text');
  const unscaledHeight = content.getBoundingClientRect().height;
  let scale = 1;
  if (unscaledHeight > {TARGET_TEXT_HEIGHT}) {{
    scale = Math.max({MIN_SCALE}, {TARGET_TEXT_HEIGHT} / unscaledHeight);
  }}
  root.style.setProperty('--layout-scale', scale.toFixed(5));
  await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
  const rect = content.getBoundingClientRect();
  document.body.dataset.posterReady = 'true';
  document.body.dataset.layoutScale = String(scale);
  document.body.dataset.textTop = String(rect.top);
  document.body.dataset.textBottom = String(rect.bottom);
}})();
</script>
</body>
</html>'''


def build_background_html():
    paper = paper_data_uri()
    return f'''<!doctype html>
<html><head><meta charset="utf-8"><style>
html,body{{margin:0;width:{CANVAS_W}px;height:{CANVAS_H}px;overflow:hidden;background:#F8F5EE;}}
img{{display:block;width:{CANVAS_W}px;height:{CANVAS_H}px;object-fit:cover;}}
</style></head><body><img src="{paper}" alt=""></body></html>'''


def _launch_browser(playwright):
    errors = []
    for executable in [None, '/usr/bin/chromium', '/usr/bin/google-chrome']:
        try:
            kwargs = {'headless': True, 'args': ['--no-sandbox', '--disable-dev-shm-usage']}
            if executable and Path(executable).exists():
                kwargs['executable_path'] = executable
            return playwright.chromium.launch(**kwargs)
        except Exception as exc:
            errors.append(str(exc))
    raise RuntimeError('Unable to launch Chromium via Playwright: ' + ' | '.join(errors[-3:]))


def render_layers(text_html, output_path: Path, text_layer_path=None, background_layer_path=None):
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        raise RuntimeError(
            'Wedding Flow Poster Lite requires Playwright + Chromium for deterministic transparent text-layer rendering. '
            'Install with: pip install playwright && playwright install chromium'
        ) from exc

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = _launch_browser(p)
        try:
            page = browser.new_page(viewport={'width': CANVAS_W, 'height': CANVAS_H}, device_scale_factor=1)
            page.set_content(text_html, wait_until='load')
            page.wait_for_function("document.body.dataset.posterReady === 'true'")

            layout = page.evaluate('''() => {
              const pick = (name) => {
                const el = document.querySelector(`[data-block="${name}"]`);
                if (!el) return null;
                const r = el.getBoundingClientRect();
                return {top:r.top,bottom:r.bottom,left:r.left,right:r.right};
              };
              return {
                scale: Number(document.body.dataset.layoutScale || '1'),
                poster: pick('poster-text'),
                names: pick('names'), info: pick('info'), dividerA: pick('divider-a'),
                start: pick('start-time'), title: pick('main-title'), dividerB: pick('divider-b'),
                flow: pick('flow'), after: pick('after-party')
              };
            }''')
            poster = layout['poster']
            if poster['top'] < 240 or poster['top'] > 265:
                raise RuntimeError(f'top-to-bottom layout invariant failed: poster top={poster["top"]:.1f}')
            if poster['bottom'] > TARGET_BOTTOM_Y + 2:
                raise RuntimeError(f'poster content exceeds bottom safety line: {poster["bottom"]:.1f} > {TARGET_BOTTOM_Y}')

            ordered = [layout[k] for k in ['names', 'info', 'dividerA', 'start', 'title', 'dividerB', 'flow', 'after'] if layout[k]]
            previous_top = -1
            for block in ordered:
                if block['top'] <= previous_top:
                    raise RuntimeError('top-to-bottom layout invariant failed: a later block rendered above an earlier block')
                previous_top = block['top']
            if layout['title'] and layout['title']['top'] > 900:
                raise RuntimeError(f'main title rendered too low ({layout["title"]["top"]:.1f}px); expected upper-middle poster region')

            with tempfile_dir() as tmpdir:
                tmp = Path(tmpdir)
                text_png = tmp / 'text-layer.png'
                bg_png = tmp / 'background-layer.png'
                page.screenshot(path=str(text_png), full_page=False, omit_background=True)

                bg_page = browser.new_page(viewport={'width': CANVAS_W, 'height': CANVAS_H}, device_scale_factor=1)
                try:
                    bg_page.set_content(build_background_html(), wait_until='load')
                    bg_page.screenshot(path=str(bg_png), full_page=False)
                finally:
                    bg_page.close()

                background = Image.open(bg_png).convert('RGBA')
                text_layer = Image.open(text_png).convert('RGBA')
                final = Image.alpha_composite(background, text_layer).convert('RGB')
                final.save(output_path, format='PNG', optimize=True)

                if text_layer_path:
                    Path(text_layer_path).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(text_png, text_layer_path)
                if background_layer_path:
                    Path(background_layer_path).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(bg_png, background_layer_path)

            return layout
        finally:
            browser.close()


class tempfile_dir:
    def __enter__(self):
        import tempfile
        self._ctx = tempfile.TemporaryDirectory(prefix='wedding-flow-poster-')
        return self._ctx.__enter__()

    def __exit__(self, exc_type, exc, tb):
        return self._ctx.__exit__(exc_type, exc, tb)


def main():
    parser = argparse.ArgumentParser(description='Render a confirmed wedding flow poster with deterministic top-to-bottom HTML/CSS typography.')
    parser.add_argument('input_json', type=Path)
    parser.add_argument('output_png', type=Path)
    parser.add_argument('--html', type=Path, help='Optionally save the transparent text-layer HTML.')
    parser.add_argument('--text-layer', type=Path, help='Optionally save the transparent PNG text layer.')
    parser.add_argument('--background-layer', type=Path, help='Optionally save the rasterized background layer.')
    args = parser.parse_args()

    data = json.loads(args.input_json.read_text(encoding='utf-8'))
    text_html = build_text_html(data)
    if args.html:
        args.html.parent.mkdir(parents=True, exist_ok=True)
        args.html.write_text(text_html, encoding='utf-8')
    render_layers(text_html, args.output_png, args.text_layer, args.background_layer)
    print(args.output_png)


if __name__ == '__main__':
    main()
