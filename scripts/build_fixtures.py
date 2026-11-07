"""Write the frozen request fixtures to prompts/ (one JSON per fixture).

Run with Strata's own Python (the active Control's, named in ~/.local/share/strata/components/control/active.json)
so the token counts use the tokenizer and chat template the server uses, for example:
  ~/.local/share/strata/components/control/0.1.56/python/bin/python3 scripts/build_fixtures.py
  ~/.local/share/strata/components/control/0.1.58/python/bin/python3 scripts/build_fixtures.py --only coding-shuri
(--only rewrites the named fixtures and their MANIFEST lines, and leaves the others as they are)

The prefill records follow standard-v1 (tools/build_standard_corpus.py), sized here for thinking-off requests.
"""
import hashlib
import itertools
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKENIZER = Path.home() / '.local/share/strata/Strata-data/packs/iq3_s/tokenizer'
SOURCE = Path.home() / 'Strata'   # the pinned source checkout (has tools/build_standard_corpus.py)
sys.path[:0] = [str(SOURCE), str(SOURCE / 'tools')]

import build_standard_corpus as SC  # noqa: E402  (standard-v1's record format and counter)

OUT = ROOT / 'prompts'
# The case marker each request starts with; the runner fills in the case id and a per-request nonce.
MARKER = '[case {case} / {nonce}]'
MARKER_SAMPLE = MARKER.format(case='T1-qwen-IQ3_S-prefill-128k', nonce='r3-s3-0123456789')
# a long fixture's document starts with its own marker, shared by its questions (so that the document is read once per seed)
LONG_MARKER = '[document {fixture} / {nonce}]'
LONG_MARKER_SAMPLE = LONG_MARKER.format(fixture='long-1M', nonce='r3-s3-0123456789')

PREFILL_TARGETS = {'prefill-4k': 4096, 'prefill-16k': 16384, 'prefill-32k': 32768, 'prefill-128k': 128000}

COPY_TEXT = (
    '港町の朝は、魚市場の競りの声から始まる。まだ空が群青色をしているうちに、漁船が一隻、また一隻と岸壁に戻ってくる。'
    '船底に並んだ発泡スチロールの箱には、氷と一緒に鯵や鯖、ときには季節外れの太刀魚が詰められている。'
    '仲買人たちは長靴の音を響かせながら箱をのぞき込み、指を二本、三本と立てて値をつける。'
    'そのやり取りは早口で、外から来た人にはほとんど聞き取れない。けれども、競りが終わる頃には、どの箱がどの店へ行くのかがきちんと決まっている。\n'
    '市場の裏手には小さな食堂がある。暖簾をくぐると、湯気の立つ味噌汁と、その日いちばん安かった魚の煮付けが出てくる。'
    '常連の漁師たちはカウンターに肩を並べ、天気図の話や、新しく入った若い船員の話をする。'
    '店の主人は黙って茶碗にご飯をよそい、ときどき話に短い相槌を打つだけだ。\n'
    '昼を過ぎると、町は急に静かになる。市場の床は水で流され、カモメだけが名残惜しそうに岸壁の上を旋回する。'
    '坂道の上の小学校からは、昼休みの子どもたちの声が風に乗って聞こえてくる。'
    '夕方、灯台に明かりがともる頃、次の漁に出る船のエンジンが一つずつかかり始める。こうして港町の一日は、終わりと始まりが重なり合いながら過ぎていく。'
)

DECODE = {
    'decode-prose-ja': '日本の四季が、人々の暮らし・食文化・年中行事にどのような影響を与えてきたかについて、具体例をたくさん交えて、2,000字以上で詳しく説明してください。',
    'decode-prose-en': 'Explain in detail, in at least 1,200 words, how a city water supply works from the source to the tap: collection, treatment, storage, distribution, pressure management, and quality monitoring. Use concrete examples.',
    'decode-json': '架空の書店の在庫データを JSON 配列で出力してください。30冊分とし、各要素は id（整数）、title、author、year（整数）、genre、price（整数、円）、stock（整数）、tags（文字列の配列）を持つこと。JSON 以外は何も出力しないこと。',
    'decode-code': 'Python で、テキストファイルを読み込んで単語の出現頻度を集計し、上位 N 件を表形式で表示するコマンドラインツールを書いてください。argparse、型ヒント、docstring を使い、pytest の単体テストも付けてください。',
    'decode-copy': '次の文章を、一字一句変えずにそのまま書き写してください。前置きや説明は付けないでください。\n\n' + COPY_TEXT,
}

GAME_PROMPT = 'マイクラ風3D箱庭ゲーム作って'
# Plain Tier 3's game since 2026-11-07 (the Minecraft prompt moved to the harness divisions); the answer is asked for as one HTML file,
# in 3D voxel art (added the same day, before any run was kept).
SHURI_PROMPT = ('Design and create a very creative, elaborate, and detailed 3D voxel art scene of Shuri Castle and its surrounding landscape in '
                'Okinawa, Japan. Include the castle architecture, nearby gates, stone walls, trees, and a rich surrounding '
                'environment. Make the scene impressive and varied and use beautiful colors. Use whatever libraries you want, '
                'but make sure I can paste it all into a single HTML file and open it in Chrome.')
CTXCOST_QUESTION = 'これらのレコードの構造を説明し、ID からレコードを探す手順と、件数が増えたときに速く探す工夫を、できるだけ詳しく書いてください。'


def count_ok(n):
    return sum(1 for k in range(1, n + 1) if k % 3 and k % 5)


def ja_puzzle():
    """A five-person ordering with exactly one solution (checked by brute force)."""
    people = ['アオイ', 'ハルト', 'ミズキ', 'ソウタ', 'ユイ']
    clues = [
        ('ハルトはミズキより前に着いた。', lambda p: p['ハルト'] < p['ミズキ']),
        ('ユイは1位でも5位でもない。', lambda p: p['ユイ'] not in (1, 5)),
        ('ソウタはアオイのすぐ後に着いた。', lambda p: p['ソウタ'] == p['アオイ'] + 1),
        ('ミズキは3位ではない。', lambda p: p['ミズキ'] != 3),
        ('アオイはユイより後に着いた。', lambda p: p['アオイ'] > p['ユイ']),
        ('ハルトは2位ではない。', lambda p: p['ハルト'] != 2),
        ('ミズキは最後ではない。', lambda p: p['ミズキ'] != 5),
    ]
    sols = []
    for perm in itertools.permutations(range(1, 6)):
        p = dict(zip(people, perm))
        if all(f(p) for _, f in clues):
            sols.append(p)
    assert len(sols) == 1, sols
    third = next(name for name, rank in sols[0].items() if rank == 3)
    text = ('5人（' + '、'.join(people) + '）が駅に到着した順番について、次のことが分かっています。\n'
            + '\n'.join('- ' + c for c, _ in clues)
            + '\n3位に到着したのは誰ですか。最後の行に「答え: 名前」の形で書いてください。')
    return text, third


def en_puzzle():
    """Three boxes, one with a prize; exactly one label is true. Unique answer checked by brute force."""
    labels = {
        'A': ('The prize is in this box.', lambda prize: prize == 'A'),
        'B': ('The prize is not in this box.', lambda prize: prize != 'B'),
        'C': ('The prize is not in box A.', lambda prize: prize != 'A'),
    }
    sols = [b for b in 'ABC' if sum(f(b) for _, f in labels.values()) == 1]
    assert len(sols) == 1, sols
    text = ('There are three boxes, A, B and C. Exactly one contains a prize. Each box has a label:\n'
            + '\n'.join(f'- Box {k}: "{v[0]}"' for k, v in labels.items())
            + '\nExactly one of the three labels is true. Which box contains the prize? '
              'End with a final line of the form "Answer: X".')
    return text, sols[0]


CODE_TESTS = '''
from solution import merge_intervals

def check():
    assert merge_intervals([]) == []
    assert merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]]) == [[1, 6], [8, 10], [15, 18]]
    assert merge_intervals([[1, 4], [4, 5]]) == [[1, 5]]
    assert merge_intervals([[5, 7], [1, 2], [2, 3]]) == [[1, 3], [5, 7]]
    assert merge_intervals([[1, 10], [2, 3], [4, 5]]) == [[1, 10]]
    assert merge_intervals([[0, 0], [0, 0]]) == [[0, 0]]
    print("PASS")

check()
'''


def tasks():
    n = 2026
    ja_text, ja_answer = ja_puzzle()
    en_text, en_answer = en_puzzle()
    return {
        'math-1': {'prompt': f'1 から {n} までの整数のうち、3 でも 5 でも割り切れないものはいくつありますか。'
                              '最後の行に「答え: 数値」の形で書いてください。',
                   'expected': {'kind': 'final_number', 'value': count_ok(n)}},
        'code-1': {'prompt': 'Write a Python function `merge_intervals(intervals: list[list[int]]) -> list[list[int]]` '
                              'that merges all overlapping or touching closed intervals and returns them sorted by start. '
                              'The input may be unsorted and may be empty; do not modify it. '
                              'Reply with the complete function in one ```python code block.',
                   'expected': {'kind': 'python_tests', 'module': 'solution', 'tests': CODE_TESTS}},
        'reason-ja-1': {'prompt': ja_text, 'expected': {'kind': 'final_text', 'value': ja_answer, 'prefix': '答え'}},
        'reason-en-1': {'prompt': en_text, 'expected': {'kind': 'final_text', 'value': en_answer, 'prefix': 'Answer'}},
    }


# Tiers 4b-4d: prompts/long-corpus.txt (scripts/long_corpus.py) cut to each length, with three made-up facts placed at
# 10 / 50 / 90 % of the document. The fixture keeps the cut and the facts, not the text: the runner puts them together.
K = 1024
ANSWER_ROOM = 512 + 256          # the answer (output cap 512) and the template, inside a context the input fills
LONG_TARGETS = {'long-32K': 32 * K, 'long-128K': 128 * K, 'long-256K': 256 * K - ANSWER_ROOM,
                'long-512K': 512 * K - ANSWER_ROOM, 'long-1M': 1024 * K - ANSWER_ROOM,
                'long-200K': 200 * K, 'long-300K': 300 * K}
PLACES = [('q-d10', 0.10, ('東の倉庫', 'the east storehouse')), ('q-d50', 0.50, ('中央の倉庫', 'the central storehouse')),
          ('q-d90', 0.90, ('西の倉庫', 'the west storehouse'))]
ANSWER_LINE = '最後の行に「答え: 数値」の形で書いてください。'


def fact_text(lang, place, code):
    ja, en = place
    return (f'（覚え書き：{ja}の合言葉は「{code}」である。）' if lang == 'ja'
            else f'(A note: the password of {en} is "{code}".)')


def long_fixtures(counter, tokens_of):
    import random
    corpus = (OUT / 'long-corpus.txt').read_text(encoding='utf-8')
    lines = corpus.split('\n')
    # tokens per line, summed: close to the count of the joined text (lines meet at a newline, a token of its own)
    per = [len(counter.tok.encode(ln + '\n')) for ln in lines]
    cum = list(itertools.accumulate(per))
    cjk = lambda t: any('\u3040' <= ch <= '\u9fff' for ch in t)  # noqa: E731
    out = {}
    for name, target in LONG_TARGETS.items():
        rnd = random.Random(name)
        codes = {q: rnd.randrange(1000, 10000) for q, _, _ in PLACES}
        questions = {q: f'上の文書のどこかに、{ja}（{en}）の合言葉が4桁の数字で書かれています。その数字は何ですか。{ANSWER_LINE}'
                     for q, _, (ja, en) in PLACES}
        questions['q-multi'] = ('上の文書には、東の倉庫と西の倉庫（the east and the west storehouse）の合言葉が、離れた2か所に4桁の数字で'
                                f'書かれています。2つの数字の和はいくつですか。{ANSWER_LINE}')
        expected = {**{q: codes[q] for q, _, _ in PLACES}, 'q-multi': codes['q-d10'] + codes['q-d90']}

        def build(n_lines):
            facts = []
            for q, at, place in PLACES:
                want = cum[n_lines - 1] * at
                i = next(j for j in range(n_lines) if cum[j] >= want)
                while i < n_lines - 1 and lines[i].strip() == '':
                    i += 1
                facts.append({'question': q, 'after_line': i, 'text': fact_text('ja' if cjk(lines[i]) else 'en', place, codes[q])})
            return facts

        def assemble(n_lines, facts):
            out_lines = list(lines[:n_lines])
            for f in sorted(facts, key=lambda f: -f['after_line']):
                out_lines.insert(f['after_line'] + 1, f['text'])
            return '\n'.join(out_lines)

        # the most lines whose request (document, facts, the longest question) stays within the target
        q_long = max(questions.values(), key=len)

        def count(n_lines):
            facts = build(n_lines)
            return facts, len(counter.ids([{'role': 'user', 'content': LONG_MARKER_SAMPLE + '\n' + assemble(n_lines, facts)
                                            + '\n\n' + MARKER_SAMPLE + '\n' + q_long}], None))
        lo = next(j for j in range(len(cum)) if cum[j] >= target * 0.9) + 1      # below the target
        hi = next(j for j in range(len(cum)) if cum[j] >= target * 1.05) + 1     # above it
        while hi - lo > 1:                                                       # the most lines that still fit
            mid = (lo + hi) // 2
            lo, hi = (mid, hi) if count(mid)[1] <= target else (lo, mid)
        n = lo
        facts, got = count(n)
        assert target * 0.98 <= got <= target, (name, got, target)
        out[name] = {'kind': 'long', 'corpus': 'long-corpus.txt', 'lines': n, 'facts': facts,
                     'questions': {q: {'question': t, 'expected': {'kind': 'final_number', 'value': expected[q], 'loose': True}}
                                   for q, t in questions.items()},
                     'target_tokens': target, 'input_tokens': got,
                     'languages': {'ja': sum(1 for ln in lines[:n] if cjk(ln)), 'lines': n}}
        print(name, n, 'lines', got, 'tokens (target', target, ')', [f['text'] for f in facts])
    return out


def write(name, data):
    data = {'fixture': name, **data}
    body = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    (OUT / f'{name}.json').write_text(body)
    return hashlib.sha256(body.encode()).hexdigest()


def main():
    only = set(sys.argv[sys.argv.index('--only') + 1].split(',')) if '--only' in sys.argv else None
    OUT.mkdir(exist_ok=True)
    template = TOKENIZER / 'chat_template.jinja'
    counter = SC.Counter(TOKENIZER, template)
    SC.TEMPLATE_KWARGS.clear()
    SC.TEMPLATE_KWARGS.update({'enable_thinking': False})

    def tokens_of(text):
        return len(counter.ids([{'role': 'user', 'content': MARKER_SAMPLE + '\n' + text}], None))

    chats = {'game-minecraft': GAME_PROMPT, 'coding-shuri': SHURI_PROMPT}
    if only:
        unknown = only - set(chats)
        if unknown:
            raise SystemExit(f'--only takes {", ".join(chats)}; not {", ".join(sorted(unknown))}')
        doc = json.loads((OUT / 'MANIFEST.json').read_text())
        for name in sorted(only):
            doc['fixtures'][name] = write(name, {'kind': 'chat', 'prompt': chats[name], 'input_tokens': tokens_of(chats[name])})
            print(name, 'written')
        (OUT / 'MANIFEST.json').write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n')
        return

    manifest = {}
    for name, target in PREFILL_TARGETS.items():
        def tok(count):
            return tokens_of(SC.records_body(count, SC.SUMMARY_QUESTION))
        lo, hi = 20, 60
        slope = (tok(hi) - tok(lo)) / (hi - lo)
        count = max(1, round(lo + (target - tok(lo)) / slope))
        for _ in range(4):
            step = round((target - tok(count)) / slope)
            if step == 0:
                break
            count += step
        best = min(range(max(1, count - 3), count + 4), key=lambda c: (abs(tok(c) - target), c))
        n = tok(best)
        assert abs(n - target) / target <= 0.02, (name, n)
        manifest[name] = write(name, {'kind': 'records', 'records': best, 'question': SC.SUMMARY_QUESTION,
                                      'record_format': SC.RECORD, 'target_tokens': target, 'input_tokens': n,
                                      'thinking': False, 'source': 'standard-v1 records_body'})
        print(name, best, 'records', n, 'tokens')
    count = json.loads((OUT / 'prefill-4k.json').read_text())['records']
    manifest['ctxcost-4k'] = write('ctxcost-4k', {'kind': 'records', 'records': count, 'question': CTXCOST_QUESTION,
                                                  'record_format': SC.RECORD, 'target_tokens': 4096,
                                                  'input_tokens': tokens_of(SC.records_body(count, CTXCOST_QUESTION)),
                                                  'thinking': False, 'source': 'standard-v1 records_body'})
    for name, text in DECODE.items():
        manifest[name] = write(name, {'kind': 'chat', 'prompt': text, 'input_tokens': tokens_of(text)})
    for name, text in chats.items():
        manifest[name] = write(name, {'kind': 'chat', 'prompt': text, 'input_tokens': tokens_of(text)})
    for name, t in tasks().items():
        manifest[name] = write(name, {'kind': 'task', 'prompt': t['prompt'], 'expected': t['expected'],
                                      'input_tokens': tokens_of(t['prompt'])})
    corpus = OUT / 'long-corpus.txt'
    if corpus.exists():
        manifest['long-corpus.txt'] = hashlib.sha256(corpus.read_bytes()).hexdigest()
        manifest['long-sources.json'] = hashlib.sha256((OUT / 'long-sources.json').read_bytes()).hexdigest()
        for name, data in long_fixtures(counter, tokens_of).items():
            manifest[name] = write(name, data)
    (OUT / 'MANIFEST.json').write_text(json.dumps({
        'marker': MARKER, 'long_marker': LONG_MARKER, 'tokenizer_dir': 'packs/iq3_s/tokenizer',
        'template_sha256': hashlib.sha256(template.read_bytes()).hexdigest(),
        'fixtures': manifest}, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
