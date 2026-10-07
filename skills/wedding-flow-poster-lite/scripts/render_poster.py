#!/usr/bin/env python3
import argparse
import base64
import html
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER_ASSET = ROOT / 'assets' / 'warm-white-paper.svg'


def esc(value):
    return html.escape(str(value or ''), quote=True)


def paper_data_uri():
    if not PAPER_ASSET.exists():
        raise FileNotFoundError(f'fixed background asset missing: {PAPER_ASSET}')
    encoded = base64.b64encode(PAPER_ASSET.read_bytes()).decode('ascii')
    return f'data:image/svg+xml;base64,{encoded}'


FORBIDDEN_FLOW_PUNCTUATION = set('，,；;：:（）()【】[]\n\r')
MAX_FLOW_ITEM_CHARS = 16


def validate_poster_data(data):
    items = [str(x).strip() for x in data.get('items', []) if str(x).strip()]
    if not items:
        raise ValueError('items must contain at least one flow item')

    for index, item in enumerate(items, start=1):
        if len(item) > MAX_FLOW_ITEM_CHARS:
            raise ValueError(
                f'flow item {index} is too verbose for Lite poster ({len(item)} chars): {item!r}. '
                f'Use one concise visible event label, preferably 2-10 Chinese characters and at most {MAX_FLOW_ITEM_CHARS} characters.'
            )
        if any(ch in FORBIDDEN_FLOW_PUNCTUATION for ch in item):
            raise ValueError(
                f'flow item {index} contains execution-note punctuation: {item!r}. '
                'Remove parenthetical notes, semicolon-separated sub-actions, staff reminders, and other backstage details before rendering.'
            )

    return items


def build_html(data):
    items = validate_poster_data(data)

    count = len(items)
    if count <= 8:
        body_size, gap = 34, 31
    elif count <= 12:
        body_size, gap = 31, 25
    elif count <= 16:
        body_size, gap = 28, 19
    else:
        body_size, gap = 25, 14

    meta = ' · '.join(esc(v) for v in [data.get('date'), data.get('startTime'), data.get('venue')] if v)
    item_html = ''.join(f'<div class="flow-item">{esc(item)}</div>' for item in items)
    names = esc(data.get('coupleNames') or '')
    title = esc(data.get('title') or '婚礼流程')
    paper = paper_data_uri()

    return f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<style>
:root {{
  --paper: #F8F5EE;
  --ink: #302D29;
  --accent: #9B4C2E;
  --flow-size: {body_size}px;
  --flow-gap: {gap}px;
}}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; }}
body {{
  background: var(--paper);
  color: var(--ink);
  font-family: "Noto Sans CJK SC", "PingFang SC", "Microsoft YaHei", Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  text-rendering: geometricPrecision;
}}
.poster {{
  width: 1080px;
  height: 1920px;
  padding: 150px 175px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  overflow: hidden;
  background-color: var(--paper);
  background-image: url("{paper}");
  background-size: 1080px 1920px;
  background-position: center;
  background-repeat: no-repeat;
}}
.names {{
  margin: 0;
  max-width: 760px;
  font-family: "Noto Serif CJK SC", "Songti SC", "STSong", serif;
  font-size: 58px;
  font-weight: 600;
  letter-spacing: .035em;
  line-height: 1.3;
}}
.meta {{
  margin-top: 28px;
  max-width: 760px;
  font-size: 21px;
  font-weight: 400;
  line-height: 1.65;
  letter-spacing: .045em;
}}
.accent {{
  width: 50px;
  height: 3px;
  margin-top: 64px;
  background: var(--accent);
}}
.title {{
  margin-top: 22px;
  font-family: "Noto Serif CJK SC", "Songti SC", "STSong", serif;
  font-size: 31px;
  font-weight: 700;
  line-height: 1.4;
  letter-spacing: .08em;
}}
.flow {{
  width: 100%;
  margin-top: 42px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--flow-gap);
}}
.flow-item {{
  max-width: 720px;
  font-size: var(--flow-size);
  line-height: 1.5;
  letter-spacing: .03em;
  color: var(--ink);
}}
</style>
</head>
<body>
<main class="poster">
  {f'<h1 class="names">{names}</h1>' if names else ''}
  {f'<div class="meta">{meta}</div>' if meta else ''}
  <div class="accent"></div>
  <div class="title">{title}</div>
  <section class="flow">{item_html}</section>
</main>
<script>
(async function fit() {{
  if (document.fonts && document.fonts.ready) await document.fonts.ready;
  const poster = document.querySelector('.poster');
  const root = document.documentElement;
  let size = parseFloat(getComputedStyle(root).getPropertyValue('--flow-size'));
  let gap = parseFloat(getComputedStyle(root).getPropertyValue('--flow-gap'));
  let guard = 0;
  while (poster.scrollHeight > poster.clientHeight && guard < 40) {{
    if (size > 20) size -= 1;
    if (gap > 8) gap -= 1;
    root.style.setProperty('--flow-size', size + 'px');
    root.style.setProperty('--flow-gap', gap + 'px');
    guard++;
  }}
  document.body.dataset.posterReady = 'true';
}})();
</script>
</body>
</html>'''


def render_png(html_text, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        sync_playwright = None

    launch_errors = []
    if sync_playwright is not None:
        try:
            with sync_playwright() as p:
                browser = None
                for executable in [None, '/usr/bin/chromium', '/usr/bin/google-chrome']:
                    try:
                        kwargs = {'headless': True, 'args': ['--no-sandbox', '--disable-dev-shm-usage']}
                        if executable and Path(executable).exists():
                            kwargs['executable_path'] = executable
                        browser = p.chromium.launch(**kwargs)
                        break
                    except Exception as exc:
                        launch_errors.append(str(exc))
                if browser is not None:
                    try:
                        page = browser.new_page(viewport={'width': 1080, 'height': 1920}, device_scale_factor=1)
                        page.set_content(html_text, wait_until='load')
                        page.wait_for_function("document.body.dataset.posterReady === 'true'")
                        page.screenshot(path=str(output_path), full_page=False)
                        return
                    finally:
                        browser.close()
        except Exception as exc:
            launch_errors.append(str(exc))

    browser_bin = next((
        shutil.which(name) for name in
        ('chromium', 'chromium-browser', 'google-chrome', 'google-chrome-stable')
        if shutil.which(name)
    ), None)
    if browser_bin:
        with tempfile.TemporaryDirectory(prefix='wedding-flow-poster-') as tmpdir:
            html_path = Path(tmpdir) / 'poster.html'
            html_path.write_text(html_text, encoding='utf-8')
            result = subprocess.run([
                browser_bin,
                '--headless',
                '--no-sandbox',
                '--disable-gpu',
                '--hide-scrollbars',
                '--force-device-scale-factor=1',
                '--window-size=1080,1920',
                f'--screenshot={output_path.resolve()}',
                html_path.resolve().as_uri(),
            ], capture_output=True, text=True)
            if result.returncode == 0 and output_path.exists():
                return
            launch_errors.append(result.stderr or result.stdout or f'Chromium exited {result.returncode}')

    detail = ' | '.join(launch_errors[-3:])
    raise RuntimeError(
        'No usable browser renderer found. Install Playwright/Chromium, or render the generated HTML with an available browser. ' + detail
    )


def main():
    parser = argparse.ArgumentParser(description='Render a confirmed wedding flow poster to PNG using real HTML/CSS text.')
    parser.add_argument('input_json', type=Path)
    parser.add_argument('output_png', type=Path)
    parser.add_argument('--html', type=Path, help='Optionally save the generated HTML alongside the PNG.')
    args = parser.parse_args()

    data = json.loads(args.input_json.read_text(encoding='utf-8'))
    html_text = build_html(data)
    if args.html:
        args.html.parent.mkdir(parents=True, exist_ok=True)
        args.html.write_text(html_text, encoding='utf-8')
    render_png(html_text, args.output_png)
    print(args.output_png)


if __name__ == '__main__':
    main()
