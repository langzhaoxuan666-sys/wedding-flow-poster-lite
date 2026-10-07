import importlib.util
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
RENDERER = ROOT / 'scripts' / 'render_poster.py'
spec = importlib.util.spec_from_file_location('renderer', RENDERER)
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)

DATA = {
    'coupleNames': '测试新郎 & 测试新娘',
    'date': '2026.10.18',
    'eventLabel': '婚礼晚宴',
    'venue': '示例酒店',
    'startTime': '11:08',
    'title': '婚礼流程',
    'items': ['主持人开场', '新人共同入场', '新人告白', '交换戒指', '父母登场', '父亲致辞', '大合影'],
    'afterPartyTitle': 'AFTER PARTY',
    'afterPartyItems': ['新人合唱', '默契挑战', '猜数字挑战', '主机游戏'],
}

html = renderer.build_text_html(DATA)
assert html.index('data-block="names"') < html.index('data-block="info"')
assert html.index('data-block="info"') < html.index('data-block="divider-a"')
assert html.index('data-block="divider-a"') < html.index('data-block="start-time"')
assert html.index('data-block="start-time"') < html.index('data-block="main-title"')
assert html.index('data-block="main-title"') < html.index('data-block="divider-b"')
assert html.index('data-block="divider-b"') < html.index('data-block="flow"')
assert html.index('data-block="flow"') < html.index('data-block="after-party"')
assert 'column-reverse' not in html
assert 'flex-direction: column;' in html

with sync_playwright() as p:
    browser = renderer._launch_browser(p)
    try:
        page = browser.new_page(viewport={'width': 1080, 'height': 1920}, device_scale_factor=1)
        page.set_content(html, wait_until='load')
        page.wait_for_function("document.body.dataset.posterReady === 'true'")
        boxes = page.evaluate('''() => ['names','info','divider-a','start-time','main-title','divider-b','flow','after-party'].map(name => {
          const e = document.querySelector(`[data-block="${name}"]`);
          const r = e.getBoundingClientRect();
          return [name, r.top, r.bottom];
        })''')
        tops = [row[1] for row in boxes]
        assert tops == sorted(tops), boxes
        d = dict((name, (top,bottom)) for name,top,bottom in boxes)
        assert 240 <= d['names'][0] <= 265, d
        assert d['main-title'][0] < 900, d
        assert d['after-party'][0] > d['flow'][0], d
    finally:
        browser.close()

print('PASS: deterministic DOM and browser geometry remain strictly top-to-bottom')
