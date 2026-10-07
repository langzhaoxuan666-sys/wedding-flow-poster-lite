import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RENDERER = ROOT / 'scripts' / 'render_poster.py'

spec = importlib.util.spec_from_file_location('renderer', RENDERER)
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)

VALID = {
    'coupleNames': '测试新郎 & 测试新娘',
    'date': '2026.10.18',
    'venue': '示例酒店',
    'startTime': '11:08',
    'title': '婚礼流程',
    'items': [
        '主持人开场',
        '新郎入场',
        '新娘入场',
        '新郎迎接',
        '新人共同入场',
        '新人告白',
        '交换戒指',
        '新人拥吻',
        '父母登场',
        '新郎父亲致辞',
        '新娘父亲致辞',
        '朋友致辞',
        '新人答谢',
        '仪式礼成',
        '大合影',
        '换装敬酒',
        '返场集体敬酒',
    ],
}

assert renderer.validate_poster_data(VALID) == VALID['items']

BAD_ITEMS = [
    '新娘入场（伴郎开门；伴娘舞台两侧）',
    '新人共同入场；随后开始新人告白',
    '返场集体敬酒（新人及伴郎伴娘撒礼物）',
]

for item in BAD_ITEMS:
    data = dict(VALID)
    data['items'] = [item]
    try:
        renderer.validate_poster_data(data)
    except ValueError as exc:
        msg = str(exc)
        assert 'concise' in msg or 'execution-note punctuation' in msg
    else:
        raise AssertionError(f'verbose flow item should be rejected: {item}')

print('PASS: concise poster content guard rejects verbose execution-note flow items')
