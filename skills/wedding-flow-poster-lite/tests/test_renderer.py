import importlib.util
import json
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RENDERER = ROOT / 'scripts' / 'render_poster.py'
PAPER = ROOT / 'assets' / 'warm-white-paper.svg'
TMP = ROOT / 'tests' / 'tmp'
TMP.mkdir(exist_ok=True)

CASES = {
    'short': [
        '主持人开场', '新郎入场', '新娘入场', '交换戒指', '合影'
    ],
    'medium': [
        '主持人开场', '新郎入场', '新娘入场', '新人告白', '交换戒指',
        '拥抱', '父母登场', '父亲致辞', '全家合影', '礼成'
    ],
    'long': [
        '主持人开场', '新郎入场', '新娘入场', '新人共同入场', '新人告白',
        '誓言', '交换戒指', '拥抱', '证婚人致辞', '父母登场', '新郎父亲致辞',
        '新娘父亲致辞', '新人致谢', '朋友祝福', '全家合影', '伴郎伴娘合影',
        '全场合影', '抛手捧花', '礼成'
    ]
}


def png_size(path: Path):
    data = path.read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n', f'{path.name} is not PNG'
    return struct.unpack('>II', data[16:24])


assert PAPER.exists(), 'fixed paper background missing'
assert PAPER.read_text(encoding='utf-8').startswith('<svg'), 'paper background must be SVG'
assert 'width="1080"' in PAPER.read_text(encoding='utf-8')
assert 'height="1920"' in PAPER.read_text(encoding='utf-8')

spec = importlib.util.spec_from_file_location('renderer', RENDERER)
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)
html_text = renderer.build_html({
    'coupleNames': '测试新郎 & 测试新娘',
    'date': '2026.10.18',
    'venue': '示例酒店',
    'startTime': '11:08',
    'title': '婚礼流程',
    'items': ['主持人开场', '新郎入场', '新娘入场'],
})
assert 'data:image/svg+xml;base64,' in html_text, 'paper asset is not embedded in HTML'
assert 'font-size: 58px;' in html_text, 'couple-name size not updated'
assert 'font-size: 21px;' in html_text, 'metadata size not updated'
assert '--ink: #302D29;' in html_text
assert '--accent: #9B4C2E;' in html_text
assert 'radial-gradient' not in html_text, 'old synthetic vignette should not remain'

for name, items in CASES.items():
    fixture = TMP / f'{name}.json'
    out = TMP / f'{name}.png'
    fixture.write_text(json.dumps({
        'coupleNames': '测试新郎 & 测试新娘',
        'date': '2026.10.18',
        'venue': '示例酒店',
        'startTime': '11:08',
        'title': '婚礼流程',
        'items': items,
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    result = subprocess.run([sys.executable, str(RENDERER), str(fixture), str(out)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr or result.stdout
    assert out.exists(), f'{name}: output missing'
    assert out.stat().st_size > 10_000, f'{name}: output suspiciously small'
    assert png_size(out) == (1080, 1920), f'{name}: wrong PNG dimensions {png_size(out)}'

print('PASS: warm-paper asset + short/medium/long fixtures render 1080x1920 PNG')
