import importlib.util
import json
import struct
import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
RENDERER = ROOT / 'scripts' / 'render_poster.py'
PAPER = ROOT / 'assets' / 'warm-white-paper.svg'
TMP = ROOT / 'tests' / 'tmp'
TMP.mkdir(exist_ok=True)

CASES = {
    'short': ['主持人开场', '新郎入场', '新娘入场', '交换戒指', '合影'],
    'medium': ['主持人开场', '新郎入场', '新娘入场', '新人告白', '交换戒指', '拥抱', '父母登场', '父亲致辞', '全家合影', '礼成'],
    'long': ['主持人开场', '新郎入场', '新娘入场', '新人共同入场', '新人告白', '誓言', '交换戒指', '拥抱', '证婚人致辞', '父母登场', '新郎父亲致辞', '新娘父亲致辞', '新人致谢', '朋友祝福', '全家合影', '伴郎伴娘合影', '全场合影', '抛手捧花', '礼成'],
}


def png_size(path: Path):
    data = path.read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n', f'{path.name} is not PNG'
    return struct.unpack('>II', data[16:24])


assert PAPER.exists(), 'fixed paper background missing'
assert PAPER.read_text(encoding='utf-8').startswith('<svg')

spec = importlib.util.spec_from_file_location('renderer', RENDERER)
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)
html_text = renderer.build_text_html({
    'coupleNames': '测试新郎 & 测试新娘',
    'date': '2026.10.18',
    'eventLabel': '婚礼晚宴',
    'venue': '示例酒店',
    'startTime': '11:08',
    'title': '婚礼流程',
    'items': ['主持人开场', '新郎入场', '新娘入场'],
    'afterPartyItems': ['新人合唱', '默契挑战'],
})
assert 'font-size: 53px;' in html_text
assert 'font-size: 33px;' in html_text
assert 'font-size: 31px;' in html_text
assert '--body-size: 28px;' in html_text
assert '--text-primary: #3B3029;' in html_text
assert '--accent: #9B4C2E;' in html_text
assert 'top: 252px;' in html_text

for name, items in CASES.items():
    fixture = TMP / f'{name}.json'
    out = TMP / f'{name}.png'
    text_layer = TMP / f'{name}-text.png'
    bg_layer = TMP / f'{name}-bg.png'
    fixture.write_text(json.dumps({
        'coupleNames': '测试新郎 & 测试新娘',
        'date': '2026.10.18',
        'eventLabel': '婚礼晚宴',
        'venue': '示例酒店',
        'startTime': '11:08',
        'title': '婚礼流程',
        'items': items,
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    result = subprocess.run([
        sys.executable, str(RENDERER), str(fixture), str(out),
        '--text-layer', str(text_layer), '--background-layer', str(bg_layer)
    ], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr or result.stdout
    assert png_size(out) == (1080, 1920)
    assert png_size(text_layer) == (1080, 1920)
    assert png_size(bg_layer) == (1080, 1920)
    alpha = Image.open(text_layer).convert('RGBA').getchannel('A')
    bbox = alpha.getbbox()
    assert bbox is not None
    assert 235 <= bbox[1] <= 275, (name, bbox)
    assert bbox[3] <= 1695, (name, bbox)

print('PASS: short/medium/long use separate layers, 1080x1920 output, top anchor and bottom safety')
