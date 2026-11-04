"""Expand the benchmark plan in docs/SCOUTING.md into one row per case, for each test environment (envs/<id>/env.json).

Per environment it writes plan/<division>/<env>/cases.jsonl and cases.csv (the case list the runner consumes) and cases/<division>/<env>.html
(the human view), and CASES.html lists the environments. The environment decides which models run, how large each model
is for its GPU memory and RAM (for the estimate only), whether the DFlash2 cases exist (the card must have DFlash2) and
the time estimate. Re-run after a benchmark run: results/<division>/<env>/<run-id>/cases/<case-id>/summary.json,
when present, fills each row's status, headline metrics and evidence links. The newest run-id wins.

    python3 -I scripts/build_cases.py              # every environment, results/ and published/ -> preview/ (not tracked)
    python3 -I scripts/build_cases.py --published  # published/ only -> CASES.html and cases/ (the committed pages)
    python3 -I scripts/build_cases.py --env <id>   # one environment's case page
"""
import os
import argparse
import csv
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from i18n import HEAD, SCRIPT, SWITCH, L, T, division_html, untranslated  # noqa: E402
import envs  # noqa: E402
import machine_info  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

# (family, model, size GB, role). How large a model is for the environment's memory: size_class() (for the estimates).
MODELS = [
    ('qwen', 'Q2_0', 67.3, '元重みの量子化 (ISTA)'),
    ('qwen', 'IQ2_XS', 68.0, '元重みの量子化 (ISTA)'),
    ('qwen', 'IQ3_XXS', 75.8, '元重みの量子化 (ISTA)'),
    ('qwen', 'IQ3_S', 83.6, '元重みの量子化 (ISTA)、基準モデル'),
    ('coder', 'IQ1_M', 58.4, 'expert 半減の剪定版'),
    ('gyro', 'Gyro-S', 58.5, '元重みの量子化 (trellis)'),
    ('gyro', 'Gyro-M', 92.0, '元重みの量子化 (trellis)'),
    ('unsloth', 'UD-IQ4_XS', 93.7, '元重みの量子化 (Unsloth)'),
    ('unsloth', 'UD-Q4_K_XL', 111.3, '元重みの量子化 (Unsloth)'),
    ('unsloth', 'UD-Q5_K_XL', 158.3, '元重みの量子化 (Unsloth)'),
    ('unsloth', 'UD-Q6_K_XL', 169.2, '元重みの量子化 (Unsloth)'),
    ('unsloth', 'Q8_0', 188.2, '元重みの量子化 (Unsloth)、品質の参照点'),
    ('swift', 'IQ2_XS', 69.1, 'fine-tune（思考が短い）'),
    ('swift', 'IQ3_XXS', 76.0, 'fine-tune（思考が短い）'),
    ('swift', 'IQ3_S', 83.7, 'fine-tune（思考が短い）'),
    ('nvfp4', 'NVFP4', 128.0, '元重みの量子化 (GPTQ)'),
    ('nvfp4', 'NVFP4-NVIDIA', 128.0, '元重みの量子化 (RTN)'),
    ('nvfp4', 'NVFP4-QAD', 102.3, 'FP4 向け再学習版'),
]
DERIVATIVE = {('coder', 'IQ1_M'), ('swift', 'IQ2_XS'), ('swift', 'IQ3_XXS'), ('swift', 'IQ3_S'),
              ('nvfp4', 'NVFP4-QAD')}
REF = ('qwen', 'IQ3_S')
TIER4B = [('qwen', 'IQ3_S'), ('qwen', 'Q2_0'), ('gyro', 'Gyro-M'), ('unsloth', 'UD-Q4_K_XL'),
          ('nvfp4', 'NVFP4'), ('unsloth', 'Q8_0')]
TIER4C = [('qwen', 'IQ3_S'), ('qwen', 'Q2_0'), ('unsloth', 'UD-Q4_K_XL')]
TIER5 = [('qwen', 'IQ3_S'), ('unsloth', 'UD-Q6_K_XL'), ('nvfp4', 'NVFP4')]

K = 1024
CTX_LABEL = {32 * K: '32K', 64 * K: '64K', 128 * K: '128K', 200 * K: '200K', 256 * K: '256K',
             384 * K: '384K', 512 * K: '512K', 768 * K: '768K', 1024 * K: '1M'}
TRAINED = 256 * K

DECODE = [('decode-prose-ja', '日本語の説明文'), ('decode-prose-en', '英語の説明文'),
          ('decode-json', '構造化出力 (JSON)'), ('decode-code', 'Python 実装'),
          ('decode-copy', '渡した文章の書き写し')]
# Lengths line up with upstream: standard-v1 and GYRO.md use 4K / 16K, community reports 4,096 / 32,768 / 128,000.
PREFILL = [('prefill-4k', 4 * K), ('prefill-32k', 32 * K), ('prefill-128k', 128000)]
# Same construction as standard-v1's frozen 4K / 16K prompts (fixed record list), extended to the other lengths.
PREFILL_CONTENT = 'standard-v1 と同じ作り方の固定レコード列'
TEMPS = [0.0, 0.7, 1.0]
# Every model's template only adds a system sentence for low / xhigh and nothing for medium; we compare off and xhigh.
EFFORTS = ['none', 'high']
TASKS = [('math-1', '数学'), ('code-1', 'コード（テスト実行で判定）'), ('reason-ja-1', '日本語の推論'),
         ('reason-en-1', '英語の推論')]
GAME_EFFORTS = ['high']
QUESTIONS = [('q-d10', '10% の位置の事実'), ('q-d50', '50% の位置の事実'), ('q-d90', '90% の位置の事実'),
             ('q-multi', '離れた複数箇所の統合')]

# Tier 5: one variable at a time from the baseline. (variable, id slug, level, launch option, note)
TIER5_VARIANTS = [
    ('baseline', 'default', '既定', '', '同じセッション内の比較基準'),
    ('drafter', 'off', 'off', '--drafting off', 'drafter なし'),
    ('spec', '2', '2', '--set spec=2', ''),
    ('spec', '6', '6', '--set spec=6', ''),
    ('spec-min-p', '0.7', '0.7', '--set spec-min-p=0.7', ''),
    ('kv', 'fp16', 'fp16', '--kv fp16', ''),
    ('kv', 'q4_0', 'q4_0', '--kv q4_0', '品質が変わる側。Tier 6 では採用しない'),
    ('prefill-chunk', '1024', '1024', '--set prefill=1024', ''),
    ('prefill-chunk', '2048', '2048', '--set prefill=2048', ''),
    ('prefill-chunk', '4096', '4096', '--set prefill=4096', ''),
    ('vram-reserve', '512', '512', '--set vram-reserve-mib=512', ''),
    ('vram-reserve', '6512', '6512', '--set vram-reserve-mib=6512', 'デスクトップアプリの保存値'),
    ('vision', 'gpu', 'gpu', '--vision gpu', '画像は入れない。エンコーダが VRAM を取る分の損失だけを見る'),
    ('pool-workers', '8', '8', '--set pool-workers=8', ''),
    ('cpu-pin', 'pcore', 'P コアのみ', '--pool-cores <P コアの論理 CPU>', 'P コア 1 つにつき 1 論理 CPU（lscpu で2スレッドを持つコア）、CPU 0 はホストスレッド用に除く。この PC では 2,4,6,8,10,12,14'),
    ('ple-io', 'mmap', 'mmap', '--set ple-io=mmap', ''),
    ('parallel', '2', '2', '--parallel 2', 'クライアント並列数も 2'),
    ('parallel', '4', '4', '--parallel 4', 'クライアント並列数も 4'),
    ('tune', 'quick', 'quick', '--tune quick --retune', 'tuner の所要時間も記録'),
    ('tune', 'thorough', 'thorough', '--tune thorough --retune', 'tuner の所要時間も記録'),
]
TIER5_CASES = ['decode-prose-ja', 'decode-code', 'prefill-4k', 'prefill-32k']
# Families whose models DFlash2 drafts (strata launch --plan on 0.1.56: Auto picks it for these; coder, swift and nvfp4
# stay on MTP). Every case pins MTP; only these models also get Tier 1's decode cases with DFlash2.
DFLASH2_FAMILIES = {'qwen', 'gyro', 'unsloth'}
DFLASH2_NOTE = '0.2.10 から Auto はこのモデルで DFlash2 を選ぶ（ほかのケースは MTP に固定）。drafter（1.2 GB）は計測前に取得しておく'

# Practical coding case: the prompt is sent verbatim, with no format instructions.
GAME_FIXTURE = 'game-minecraft'
GAME_PROMPT = 'マイクラ風3D箱庭ゲーム作って'
GAME_NOTE = ('成果物は artifact/ に展開（response.md、files/、manifest.json、静的 HTML なら screenshot.png）。'
             '形式（単体 HTML / 要サーバー / README の有無）は manifest に記録')

# Time model for the estimate. Seconds and tokens/s. Fitted to the first full run on rtx5090-128g (2026-11-03-main:
# medians of the measured requests and launches); another card overrides what differs in its env.json "assume".
# Over 256K input was not measured yet (Tier 4b/4c).
ASSUME = {
    'decode_tps': {'small': 240, 'edge': 100, 'large': 80, 'nvfp4': 165},
    'prefill_tps': [(8 * 1024, 3200), (64 * 1024, 5700), (256 * 1024, 6000), (None, 2500)],
    'prefill_factor': {'edge': 0.4, 'large': 0.35, 'nvfp4': 0.6},
    'launch_base_s': 20,
    'launch_s_per_gb': 0.45,
    'launch_extra_s': {'edge': 60},
    'tune_s_per_gb': {'quick': 4.5, 'thorough': 20},
    'warmup_s': 8,
    'request_overhead_s': 0.2,
    'reasoning_tokens': {'none': 0, 'low': 50, 'medium': 100, 'high': 150, 'xhigh': 200},
    'game_reasoning_tokens': {'none': 0, 'low': 3000, 'medium': 6000, 'high': 10000},
    'game_answer_tokens': 14500,
    'task_answer_tokens': 550,
    'long_answer_tokens': 150,
    'sanity_output_tokens': 150,
    'standard_runs': 3,                 # Tier 2: the suite runs 3 times, each on its own engine
    'long_cached_tokens': 16384,        # Tiers 4b-4d: what a later question reuses of the document (one checkpoint)
    'standard_run_overhead_s': 60,      # per run, on top of the launch: the suite's own warm-up and checks
}


def yarn(ctx):
    return f'{ctx / TRAINED:g}' if ctx > TRAINED else ''


def base(tier, step, fam, model, **kw):
    row = dict(tier=tier, step=step, family=fam, model=model, context=128 * K, yarn='',
               launch_opts='', config='baseline', fixture='', content='', input_tokens='',
               output_cap='', effort='none', temperature=0.7, concurrency=1, reps=3,
               seeds='1,2,3', timeout_s=1800, measures='', note='', restarts=1, artifact=False)
    row.update(kw)
    row['context_label'] = CTX_LABEL.get(row['context'], str(row['context']))
    if 'yarn' not in kw:
        row['yarn'] = yarn(row['context'])
    row['id'] = '-'.join(str(x) for x in [f"T{step}", fam, model, row.pop('_key')])
    return row


def thinking_budget(cap):
    """The budget Strata's answer_room would pick for this cap (serve/server.py), sent explicitly instead."""
    return cap - min(max(512, cap // 4), cap // 2)


def effort_note(effort, cap, game=False):
    if effort == 'none':
        return 'thinking off: reasoning_effort "none" + chat_template_kwargs.enable_thinking false'
    return (f'thinking on: reasoning_effort "xhigh" + chat_template_kwargs.enable_thinking true、'
            f'reasoning_budget_tokens {(cap // 2 if game else thinking_budget(cap)):,}（明示'
            + ('。ゲームは cap の半分: 3/4 だと回答のコードが途中で切れたため）' if game else '）'))


def game_case(tier, step, fam, model, effort, temperature, cap, timeout):
    return base(tier, step, fam, model, _key=f'{GAME_FIXTURE}-{effort}', fixture=GAME_FIXTURE,
                content=f'「{GAME_PROMPT}」（実用的なコーディング）', input_tokens='短文', output_cap=cap,
                effort=effort, temperature=temperature, timeout_s=timeout, artifact=True,
                measures='完了時間, 出力 token, cap 到達, 成果物が動くか',
                note=effort_note(effort, cap, game=True) + '。' + GAME_NOTE)


def tier1_cases(tier, step, fam, model, **kw):
    rows = []
    for fx, content in DECODE:
        for t in TEMPS:
            rows.append(base(tier, step, fam, model, _key=f'{fx}-t{t:g}', fixture=fx, content=content,
                             input_tokens='短文', output_cap=512, temperature=t,
                             measures='decode tok/s, MTP 採用率', **kw))
    for fx, n in PREFILL:
        rows.append(base(tier, step, fam, model, _key=fx, fixture=fx, content=PREFILL_CONTENT,
                         input_tokens=n, output_cap=128, measures='prefill tok/s, TTFT, 長文後の decode', **kw))
    return rows


def build(cfg):
    use_env(cfg)
    names = {(f, m) for f, m, *_ in env_models()}
    rows = []
    # Tier 0: instrument check on IQ3_S across 3 engine restarts, plus the author's protocol on Gyro-S.
    for r in tier1_cases('0', '0', *REF):
        r.update(reps=9, seeds='1,2,3 × 起動 3 回', restarts=3, note='起動間のばらつきを測る。反復回数の決定に使う')
        rows.append(r)
    for fx, content in [('decode-prose-en', 'Prose'), ('decode-json', 'JSON'), ('decode-code', 'Code'),
                        ('decode-copy', 'Copy')]:
        rows.append(base('0', '0', 'gyro', 'Gyro-S', _key=f'author-{fx}', config='author-protocol', fixture=fx,
                         content=content, input_tokens='短文', output_cap=512,
                         measures='decode tok/s を GYRO.md の 5090 の値と比較',
                         note='sampling は作者の値: top-k 20 / top-p 0.95 / min-p 0.05'))
    for fx, n in [('prefill-4k', 4 * K), ('prefill-16k', 16 * K)]:  # the lengths GYRO.md reports
        rows.append(base('0', '0', 'gyro', 'Gyro-S', _key=f'author-{fx}', config='author-protocol', fixture=fx,
                         content=PREFILL_CONTENT, input_tokens=n, output_cap=128,
                         measures='prefill tok/s を GYRO.md の 5090 の値と比較',
                         note='sampling は作者の値: top-k 20 / top-p 0.95 / min-p 0.05'))
    rows.append(game_case('0', '0', *REF, 'none', 0.7, 16384, 1800))
    rows[-1]['note'] = '成果物の展開・スクリーンショットの仕組みを確かめる。' + rows[-1]['note']

    for fam, model, *_ in env_models():
        rows += tier1_cases('1', '1', fam, model)
        # The same decode cases with DFlash2, in a launch of their own, where the model has it (the rest pin MTP).
        if fam in DFLASH2_FAMILIES and 'dflash2' in cfg['drafters']:
            for fx, content in DECODE:
                for t in TEMPS:
                    rows.append(base('1', '1', fam, model, _key=f'dflash2-{fx}-t{t:g}', config='drafter=DFlash2',
                                     launch_opts='--drafting dflash2', fixture=fx, content=content, input_tokens='短文',
                                     output_cap=512, temperature=t, measures='decode tok/s, DFlash2 採用率',
                                     note=DFLASH2_NOTE))

    for fam, model, *_ in env_models():
        label = 'derivative（公式比較外）' if (fam, model) in DERIVATIVE else 'conforming'
        for fx, n in [('short', 77), ('prompt-4k', 4093), ('prompt-16k', 16386)]:
            rows.append(base('2', '2', fam, model, _key=f'std-{fx}', config='standard-v1', fixture=f'performance-{fx}',
                             content='standard-v1 固定 fixture', input_tokens=n, output_cap=512, effort='xhigh',
                             temperature=1.0, measures='prefill / decode / 回答までの時間', note=label))
        for cat, name in [('I', 'instruction'), ('R', 'retrieval'), ('T', 'tool_call')]:
            for i in range(1, 5):
                rows.append(base('2', '2', fam, model, _key=f'std-sanity-{cat}{i}', config='standard-v1',
                                 fixture=f'sanity-{cat}{i}', content=name, input_tokens='固定', output_cap=2048,
                                 effort='xhigh', temperature=1.0, seeds='1（スイートを 3 回実行）',
                                 measures='正答', note=label))

    for fam, model, *_ in env_models():
        for task, content in TASKS:
            for eff in EFFORTS:
                rows.append(base('3', '3', fam, model, _key=f'{task}-{eff}', fixture=task, content=content,
                                 input_tokens='短文', output_cap=16384, effort=eff, temperature=1.0,
                                 measures='思考 token 数, 回答までの時間, 完了時間, 正答, cap 到達',
                                 note=effort_note(eff, 16384)))
        for eff in GAME_EFFORTS:
            rows.append(game_case('3', '3', fam, model, eff, 1.0, 32768, 3600))

    for fam, model, *_ in env_models():
        for ctx in [128 * K, 256 * K, 1024 * K]:
            rows.append(base('4', '4a', fam, model, _key=f'ctxcost-{CTX_LABEL[ctx]}', context=ctx,
                             fixture='ctxcost-4k', content='4K の文章 + 続きを書く指示', input_tokens=4 * K,
                             output_cap=512, measures='decode tok/s, expert cache スロット数, VRAM / RAM peak, 起動可否'))

    def long_rows(step, models, lengths, ctx_of, timeout):
        out = []
        for fam, model in models:
            for n, label in lengths:
                for q, content in QUESTIONS:
                    first = q == QUESTIONS[0][0]
                    out.append(base('4', step, fam, model, _key=f'long-{label}-{q}', context=ctx_of(n),
                                    fixture=f'long-{label}', content=content, input_tokens=n, output_cap=512,
                                    timeout_s=timeout,
                                    measures=('prefill tok/s, TTFT, 長文後の decode, RAM / VRAM peak, 正答'
                                              if first else '正答（文書部分は prefix cache を使う）')))
        return out

    rows += long_rows('4b', TIER4B, [(32 * K, '32K'), (128 * K, '128K'), (TRAINED, '256K')],
                      lambda n: TRAINED, 1800)
    rows += long_rows('4c', TIER4C, [(512 * K, '512K'), (1024 * K, '1M')],
                      lambda n: n, 7200)
    for n, label, arms in [(300 * K, '300K', [(384 * K, 'yarn1.5', '', 'factor 1.5'),
                                              (384 * K, 'none', '--set rope-scaling=none', 'YaRN なし（学習長超え）')]),
                           (200 * K, '200K', [(256 * K, 'none', '', 'YaRN なし'),
                                              (1024 * K, 'yarn4', '', 'factor 4')])]:
        for ctx, arm_id, opts, arm in arms:
            for q, content in QUESTIONS:
                extra = {'yarn': 'なし'} if arm_id == 'none' else {}
                rows.append(base('4', '4d', *REF, _key=f'yarn-{label}-ctx{CTX_LABEL[ctx]}-{arm_id}-{q}',
                                 context=ctx, launch_opts=opts, **extra, **({'config': 'rope-scaling=none'} if opts else {}), fixture=f'long-{label}', content=content, input_tokens=n,
                                 output_cap=512, timeout_s=7200, measures='正答, prefill / decode tok/s',
                                 note=arm + ('。rope の flag 名は engine の解決済み設定で確認する' if opts else '')))

    for fam, model in TIER5:
        for var, slug, level, opts, note in TIER5_VARIANTS:
            for fx in TIER5_CASES:
                is_prefill = fx.startswith('prefill')
                n = dict(PREFILL).get(fx, '短文')
                conc = int(level) if var == 'parallel' else 1
                rows.append(base('5', '5', fam, model, _key=f'{var}-{slug}-{fx}',
                                 config=f'{var}={level}', launch_opts=opts, fixture=fx,
                                 content=PREFILL_CONTENT if is_prefill else dict(DECODE)[fx],
                                 input_tokens=n, output_cap=128 if is_prefill else 512, concurrency=conc,
                                 measures='prefill tok/s, TTFT' if is_prefill else 'decode tok/s, MTP 採用率',
                                 note=note))

    rows = [r for r in rows if (r['family'], r['model']) in names]   # Tiers 0, 4 and 5 name their models directly
    ids = [r['id'] for r in rows]
    assert len(ids) == len(set(ids)), 'duplicate case id'
    for r in rows:
        r['env'] = cfg['id']
        r['size_class'] = size_class(SIZE[(r['family'], r['model'])], cfg)
        r['session'] = session_of(r)
    # the runner sends up to 3 seeds of a case on every start of its session, and a session starts as often as its
    # case with the most restarts asks (Tier 0: a 1-restart case beside 3-restart ones is measured 3 times)
    starts = {}
    for r in rows:
        starts[(r['step'], r['session'])] = max(starts.get((r['step'], r['session']), 0), r['restarts'])
    for r in rows:
        if r['step'] == '2':
            n = r['reps'] * (1 if r['fixture'].startswith('sanity-') else ASSUME_ENV['standard_runs'])
        else:
            n = min(r['reps'], 3) * starts[(r['step'], r['session'])]
        r['requests'] = n
        r['est_s'] = round(request_seconds(r) * n)
    return rows


def session_of(r):
    """Cases with the same model, context and launch options share one engine start."""
    parts = ['S0' if r['step'] == '0' else 'S', r['family'], r['model'], r['context_label']]
    if r['launch_opts']:
        parts.append(r['config'].replace('=', '-').replace(' ', ''))
    return '-'.join(parts)


SIZE = {(f, m): gb for f, m, gb, _ in MODELS}
GIB = 1.073741824   # GB per GiB


def size_class(gb, cfg):
    """A model of gb GB against this environment's RAM + GPU memory, for the time estimates only (ASSUME): 'small' up to
    80%, 'edge' up to 100%, 'large' past it. Not shown on the pages: where the engine actually keeps the weights is its own
    business, and the measured speeds say more than this guess."""
    hw = cfg.get('hardware') or {}
    total = ((hw.get('ram_gib') or 0) + (hw.get('gpu_vram_gib') or 0)) * GIB
    if not total or gb <= 0.8 * total:
        return 'small'
    return 'edge' if gb <= total else 'large'


# Set by use_env(): the environment the plan is being built for.
ENV = None
ASSUME_ENV = ASSUME


def use_env(cfg):
    global ENV, ASSUME_ENV
    ENV = cfg
    ASSUME_ENV = {**ASSUME, **(cfg.get('assume') or {})}


def env_models():
    """The models this environment runs: every model, or the ones env.json lists."""
    keep = ENV.get('models') if ENV else None
    return [m for m in MODELS if not keep or f'{m[0]} {m[1]}' in keep]


def speeds(r):
    decode = ASSUME_ENV['decode_tps']['nvfp4' if r['family'] == 'nvfp4' else r['size_class']]
    return r['size_class'], decode


def prefill_seconds(r, tokens):
    where, _ = speeds(r)
    tps = next(v for limit, v in ASSUME_ENV['prefill_tps'] if limit is None or tokens <= limit)
    key = 'nvfp4' if r['family'] == 'nvfp4' else where
    return tokens / (tps * ASSUME_ENV['prefill_factor'].get(key, 1))


def request_seconds(r):
    _, decode = speeds(r)
    a = ASSUME_ENV
    tokens_in = r['input_tokens'] if isinstance(r['input_tokens'], int) else 300
    out = r['output_cap'] or 512
    fx = r['fixture']
    if fx == GAME_FIXTURE:
        out = min(out, a['game_reasoning_tokens'][r['effort']] + a['game_answer_tokens'])
    elif r['step'] == '3':
        out = min(out, a['reasoning_tokens'][r['effort']] + a['task_answer_tokens'])
    elif fx.startswith('sanity-'):
        out = a['sanity_output_tokens']
    elif fx.startswith('long-'):
        out = a['long_answer_tokens']
        if not r['id'].endswith('q-d10'):
            # the later questions reuse the document from the prefix cache, but only its first checkpoint (16K in the
            # test of 4b at 32K on the RTX 5090): the rest is read again
            tokens_in = max(300, tokens_in - a['long_cached_tokens'])
    return prefill_seconds(r, tokens_in) + out / decode + a['request_overhead_s']


def launch_seconds(r):
    gb = SIZE[(r['family'], r['model'])]
    a = ASSUME_ENV
    s = a['launch_base_s'] + gb * a['launch_s_per_gb'] + a['launch_extra_s'].get(r['size_class'], 0)
    for level, per_gb in a['tune_s_per_gb'].items():
        if f'--tune {level}' in r['launch_opts']:
            s += gb * per_gb
    return s + a['warmup_s']


def estimate(rows):
    # Every Tier starts its own sessions (sessions/<session>-T<step>), even one another Tier also uses.
    # Tier 2 has no runner sessions: strata bench starts an engine for each of the suite's runs.
    launches = {}
    for r in rows:
        if r['step'] == '2':
            sec = ASSUME_ENV['standard_runs'] * (launch_seconds(r) + ASSUME_ENV['standard_run_overhead_s'])
            launches[(r['step'], r['family'], r['model'])] = sec
        else:
            key = (r['step'], r['session'])
            launches[key] = max(launches.get(key, 0), r['restarts'] * launch_seconds(r))
    per_step = {}
    for r in rows:
        s = per_step.setdefault(r['step'], {'request_s': 0, 'launch_s': 0})
        s['request_s'] += r['est_s']
    for (step, *_), sec in launches.items():
        per_step[step]['launch_s'] += sec
    for s in per_step.values():
        s['total_h'] = round((s['request_s'] + s['launch_s']) / 3600, 1)
    return per_step


def attach_results(rows, env_id, published_only=False):
    by_id = {}
    for run in envs.run_dirs(env_id, published_only):   # sorted, so the newest run-id is kept; no test- runs
        for summary in sorted(run.glob('cases/*/summary.json')):
            by_id[summary.parent.name] = summary
    for r in rows:
        summary = by_id.get(r['id'])
        r['status'] = 'planned'
        r['result'] = {}
        r['evidence'] = []
        if not summary:
            continue
        try:
            data = json.loads(summary.read_text())
        except (OSError, ValueError):
            data = {'status': 'unreadable'}
        r['status'] = data.get('status', 'done')
        r['result'] = {k: data[k] for k in ['prefill_tps', 'decode_tps', 'ttft_ms', 'first_answer_ms',
                                            'total_ms', 'reasoning_tokens', 'accept_rate', 'correct', 'n']
                       if k in data}
        r['run_id'] = summary.parents[2].name
        case_dir = summary.parent
        r['evidence'] = [str(p.relative_to(ROOT)) for p in sorted(case_dir.iterdir()) if p.is_file()]
        art = case_dir / 'artifact'
        if art.is_dir():
            # Per seed: entry points first, then the folder itself, whatever layout the model chose.
            for seed_dir in sorted(art.glob('seed-*')) or [art]:
                for name in ['screenshot.png', 'manifest.json', 'response.md']:
                    if (seed_dir / name).exists():
                        r['evidence'].append(str((seed_dir / name).relative_to(ROOT)))
                r['evidence'] += [str(p.relative_to(ROOT)) for p in sorted(seed_dir.glob('files/**/index.html'))[:1]]
                r['evidence'].append(str(seed_dir.relative_to(ROOT)) + '/')


COLUMNS = [
    ('id', 'case id'), ('step', 'Tier'), ('family', 'family'), ('model', 'model'),
    ('context_label', 'context'), ('yarn', 'YaRN'), ('config', '設定'), ('launch_opts', '起動オプションの差分'),
    ('fixture', 'fixture'), ('content', '入力の内容'), ('input_tokens', '入力 token'), ('output_cap', '出力 cap'),
    ('effort', 'effort'), ('temperature', 'temp'), ('concurrency', '並列'), ('reps', '回数'),
    ('seeds', 'seed'), ('timeout_s', 'timeout s'), ('measures', '見るもの'), ('note', '備考'),
    ('session', '起動セッション'), ('est_s', '見積 s'),
]
# The page's column headings (CASES.html); cases.csv keeps the keys.
HEADINGS = {
    '設定': ('config', '配置'), '起動オプションの差分': ('launch options (vs. default)', '启动选项（相对默认）'),
    '入力の内容': ('input', '输入内容'), '入力 token': ('input tokens', '输入 token'), '出力 cap': ('output cap', '输出 cap'),
    '並列': ('concurrency', '并发'), '回数': ('runs', '次数'), '見るもの': ('measures', '测量内容'), '備考': ('notes', '备注'),
    '起動セッション': ('launch session', '启动会话'), '見積 s': ('est. s', '预估 s'),
}
# Session names are directory names, so they stay as they are.
UNTRANSLATED_COLS = {'id', 'session'}


TIER_INFO = {
    '0': ('計測器の検証（IQ3_S × 起動3回、Gyro-S で作者の値と照合、ゲーム作成の展開確認）',
          'validating the harness (IQ3_S × 3 launches, Gyro-S against the author\'s figures, unpacking the game result)',
          '验证测量工具（IQ3_S × 启动 3 次、用 Gyro-S 对照作者的数值、确认游戏成果的展开）'),
    '1': ('18モデルの基礎速度（decode 5種 × temperature 3水準、prefill 4K / 32K / 128K）。decode は DFlash2 対応の11モデルで DFlash2 でも測る',
          'base speed of 18 models (5 decode kinds × 3 temperatures, prefill 4K / 32K / 128K); decode also with DFlash2 on the 11 models that have it',
          '18 个模型的基础速度（decode 5 种 × temperature 3 档，prefill 4K / 32K / 128K）；支持 DFlash2 的 11 个模型的 decode 也用 DFlash2 测量'),
    '2': ('公式 standard-v1（thinking xhigh、temperature 1.0）をスイートごと3回',
          'the official standard-v1 (thinking xhigh, temperature 1.0), the whole suite 3 times',
          '官方 standard-v1（thinking xhigh，temperature 1.0），整个套件 3 次'),
    '3': ('推論エフォート none / high × 4問、ゲーム作成は high のみ（18モデル）',
          'reasoning effort none / high × 4 tasks, the game at high only (18 models)',
          '推理 effort none / high × 4 题，游戏制作仅 high（18 个模型）'),
    '4a': ('容量の確保コスト（128K / 256K / 1M に同じ 4K 入力）',
           'the cost of reserving context (the same 4K input at 128K / 256K / 1M)',
           '预留上下文的代价（128K / 256K / 1M 下相同的 4K 输入）'),
    '4b': ('学習範囲の長文（32K / 128K / 256K、代表6）', 'long inputs within the trained length (32K / 128K / 256K, 6 models)',
           '训练长度内的长文本（32K / 128K / 256K，代表 6 个）'),
    '4c': ('拡張範囲の長文（512K / 1M、代表3）', 'long inputs in the extended range (512K / 1M, 3 models)',
           '扩展范围的长文本（512K / 1M，代表 3 个）'),
    '4d': ('YaRN の影響（IQ3_S、同じ入力で設定だけ変える）', 'the effect of YaRN (IQ3_S, same input, only the setting changes)',
           'YaRN 的影响（IQ3_S，相同输入只改设置）'),
    '5': ('起動オプションを1つずつ変える（代表3、自動 tune を含む）', 'changing one launch option at a time (3 models, auto tune included)',
          '每次只改一个启动选项（代表 3 个，含自动 tune）'),
}
NUM_COLS = {'input_tokens', 'output_cap', 'temperature', 'concurrency', 'reps', 'timeout_s', 'est_s'}
WRAP_COLS = {'launch_opts', 'content', 'measures', 'note'}


def cell(v, key):
    if isinstance(v, bool):
        return '✓' if v else ''
    if isinstance(v, int) and key != 'temperature':
        return f'{v:,}'
    return '' if v is None else str(v)


def result_text(r):
    m = r.get('result') or {}
    labels = [('prefill_tps', 'prefill'), ('decode_tps', 'decode'), ('ttft_ms', 'TTFT ms'),
              ('accept_rate', L('採用率', 'acceptance', '接受率')), ('reasoning_tokens', L('思考', 'thinking', '思考')),
              ('correct', L('正答', 'correct', '正确'))]
    return ' / '.join(f'{label} {html.escape(str(m[k]))}' for k, label in labels if m.get(k) is not None)


def write_html(rows, path, cfg, published_only=False):
    """cases/<division>/<env>.html (or preview/cases/<division>/<env>.html): links to the result files are relative to where the page is."""
    e = html.escape
    up = os.path.relpath(ROOT, path.parent) + '/'
    est = estimate(rows)
    sessions = {}
    for r in rows:
        sessions[r['session']] = max(sessions.get(r['session'], 0), r['restarts'])
    total_h = sum(s['total_h'] for s in est.values())
    done = sum(r['status'] == 'done' for r in rows)
    failed = sum(r['status'] in ('failed', 'unreadable') for r in rows)
    cards = ''.join(f'<div class="card"><div class="k">{k}</div><div class="v">{v}</div></div>' for k, v in [
        (L('ケース', 'cases', '用例'), f'{len(rows):,}'),
        (L('本計測リクエスト', 'measured requests', '正式测量请求'), f'{sum(r["requests"] for r in rows):,}'),
        (L('エンジン起動', 'engine launches', '引擎启动'), f'{sum(sessions.values()):,}'),
        (L('見積もり', 'estimate', '预估'), f'{total_h:.0f} ' + L('時間', 'h', '小时')),
        (L('完了', 'done', '完成'), done), (L('失敗', 'failed', '失败'), failed)])

    tier_rows = []
    for step in dict.fromkeys(r['step'] for r in rows):
        lst = [r for r in rows if r['step'] == step]
        tier_rows.append(
            f'<tr><td><a href="#cases" data-step="{e(step)}">{e(step)}</a></td><td>{L(*TIER_INFO[step]) if step in TIER_INFO else ""}</td>'
            f'<td class="num">{len({(r["family"], r["model"]) for r in lst})}</td><td class="num">{len(lst):,}</td>'
            f'<td class="num">{sum(r["reps"] for r in lst):,}</td>'
            f'<td class="num">{est[step]["total_h"]}</td>'
            f'<td class="num">{sum(r["status"] == "done" for r in lst)}</td></tr>')
    tiers = (f'<tr><th>Tier</th><th>{L("内容", "what", "内容")}</th><th class="num">{L("モデル", "models", "模型")}</th>'
             f'<th class="num">{L("ケース", "cases", "用例")}</th><th class="num">{L("リクエスト", "requests", "请求")}</th>'
             f'<th class="num">{L("見積 h", "est. h", "预估 h")}</th><th class="num">{L("完了", "done", "完成")}</th></tr>'
             + ''.join(tier_rows))

    models = (f'<tr><th>family</th><th>model</th><th class="num">GB</th><th>{L("種別", "kind", "类别")}</th></tr>'
              + ''.join(f'<tr><td>{f}</td><td>{m}</td><td class="num">{gb}</td><td>{T(role)}</td></tr>'
                        for f, m, gb, role in env_models()))

    def heading(label):
        return L(label, *HEADINGS[label]) if label in HEADINGS else e(label)
    thead = (f'<tr><th>{L("状態", "status", "状态")}</th>' + ''.join(
        f'<th class="{"num" if k in NUM_COLS else ""}">{heading(label)}</th>' for k, label in COLUMNS)
        + f'<th>{L("結果", "result", "结果")}</th><th>{L("エビデンス", "evidence", "证据")}</th></tr>')
    body = []
    for r in rows:
        tds = []
        for k, _ in COLUMNS:
            cls = 'id' if k == 'id' else 'num' if k in NUM_COLS else 'wrap' if k in WRAP_COLS else ''
            text = cell(r[k], k)
            tds.append(f'<td class="{cls}">{e(text) if k in UNTRANSLATED_COLS else T(text)}</td>')
        ev = ''.join(f'<a href="{up}{e(x)}">{e(x.rstrip("/").split("/")[-1] + ("/" if x.endswith("/") else ""))}</a>'
                     for x in r['evidence'])
        if r.get('run_id'):
            ev += f'<div class="muted">{e(r["run_id"])}</div>'
        body.append(f'<tr data-step="{e(r["step"])}" data-model="{e(r["family"] + " " + r["model"])}" '
                    f'data-status="{e(r["status"])}" data-reps="{r["reps"]}">'
                    f'<td><span class="badge s-{e(r["status"])}">{e(r["status"])}</span></td>{"".join(tds)}'
                    f'<td class="wrap">{result_text(r)}</td><td class="ev">{ev}</td></tr>')

    def options(values):
        return ''.join(f'<option>{e(v)}</option>' for v in values)

    page = Path(__file__).with_name('cases_template.html').read_text()
    path.parent.mkdir(parents=True, exist_ok=True)
    for key, value in {
        'generated': e(__import__('datetime').datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %Z')),
        'cards': cards, 'tiers': tiers, 'models': models, 'thead': thead, 'tbody': '\n'.join(body),
        'assume': e(json.dumps(ASSUME, ensure_ascii=False, indent=2)), 'game_prompt': e(GAME_PROMPT),
        'opt_step': options(dict.fromkeys(r['step'] for r in rows)),
        'opt_model': options(f'{f} {m}' for f, m, *_ in env_models()),
        'opt_status': options(dict.fromkeys(['planned', 'done', 'failed', 'skipped'] + [r['status'] for r in rows])),
        'count': f'{len(rows):,} cases / {sum(r["reps"] for r in rows):,} requests',
        'i18n_head': HEAD, 'lang_switch': SWITCH, 'i18n_script': SCRIPT,
        'env': machine_info.env_box(ROOT, cfg, published_only),
        'mode_note': '' if published_only else PREVIEW_NOTE, 'env_label': e(envs.label(cfg)), 'env_id': e(cfg['id']),
        'division': division_html(envs.load_division(envs.division()), up), 'division_id': e(envs.division()), 'up': e(up),
    }.items():
        page = page.replace('{{' + key + '}}', value)
    path.write_text(page)


PREVIEW_NOTE = ('<p class="preview">' + L('プレビュー: 計測中・公開前（results/）の結果も含む。公開するページは scripts/publish.py で published/ に移した結果だけから作る。',
                                             'Preview: includes results still in results/ (measuring, not published). The published pages are built only from runs moved to published/ by scripts/publish.py.',
                                             '预览：包含 results/ 中尚在测量、未发布的结果。发布的页面只由 scripts/publish.py 移到 published/ 的结果生成。') + '</p>')


def write_plan(rows, env_id):
    out = envs.plan_dir(env_id)
    out.mkdir(parents=True, exist_ok=True)
    with (out / 'cases.jsonl').open('w') as f:
        for r in rows:
            f.write(json.dumps({k: v for k, v in r.items() if k not in ('result', 'evidence', 'status', 'run_id')},
                               ensure_ascii=False) + '\n')
    with (out / 'cases.csv').open('w', newline='') as f:
        w = csv.writer(f)
        w.writerow([k for k, _ in COLUMNS])
        for r in rows:
            w.writerow([r[k] for k, _ in COLUMNS])


def write_index(summaries, out_root):
    """CASES.html: the environments, each with its plan's size and progress, linking to cases/<division>/<env>.html."""
    e = html.escape
    head = (f'<tr><th>{L("環境", "environment", "环境")}</th><th>id</th><th class="num">{L("ケース", "cases", "用例")}</th>'
            f'<th class="num">{L("見積 h", "est. h", "预估 h")}</th><th class="num">{L("完了", "done", "完成")}</th>'
            f'<th class="num">{L("失敗", "failed", "失败")}</th><th>{L("最新の RUN_ID", "latest RUN_ID", "最新 RUN_ID")}</th></tr>')
    body = ''.join(
        f'<tr><td><a href="cases/{e(envs.division())}/{e(x["id"])}.html">{e(x["label"])}</a>{" ★" if x["here"] else ""}</td><td><code>{e(x["id"])}</code></td>'
        f'<td class="num">{x["cases"]:,}</td><td class="num">{x["hours"]:.0f}</td><td class="num">{x["done"]:,}</td>'
        f'<td class="num">{x["failed"]:,}</td><td>{e(x["run"] or "–")}</td></tr>' for x in summaries)
    page = Path(__file__).with_name('cases_index_template.html').read_text()
    up = os.path.relpath(ROOT, out_root) + '/' if out_root != ROOT else ''
    for key, value in {'mode_note': '' if out_root == ROOT else PREVIEW_NOTE, 'rows': head + body,
                       'division': division_html(envs.load_division(envs.division()), up), 'i18n_head': HEAD, 'lang_switch': SWITCH, 'i18n_script': SCRIPT,
                       'generated': e(__import__('datetime').datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %Z'))}.items():
        page = page.replace('{{' + key + '}}', value)
    out_root.mkdir(parents=True, exist_ok=True)
    (out_root / 'CASES.html').write_text(page)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--env', default='', help='only this environment (default: every one in envs/)')
    ap.add_argument('--published', action='store_true',
                    help='only the runs in published/, written to CASES.html and cases/ (default: also results/, to preview/)')
    a = ap.parse_args()
    out_root = ROOT if a.published else envs.PREVIEW
    here = envs.detect()[0]
    summaries = []
    for env_id in envs.ids():
        cfg = envs.load(env_id)
        rows = build(cfg)
        attach_results(rows, env_id, a.published)
        est = estimate(rows)
        hours = sum(s['total_h'] for s in est.values())
        runs = sorted({r['run_id'] for r in rows if r.get('run_id')})
        summaries.append({'id': env_id, 'label': envs.label(cfg), 'here': env_id == here, 'cases': len(rows), 'hours': hours,
                          'done': sum(r['status'] == 'done' for r in rows),
                          'failed': sum(r['status'] in ('failed', 'unreadable') for r in rows), 'run': runs[-1] if runs else None})
        if a.env and env_id != a.env:
            continue
        write_plan(rows, env_id)
        write_html(rows, out_root / 'cases' / envs.division() / f'{env_id}.html', cfg, a.published)
        missing = untranslated([r[k] for r in rows for k, _ in COLUMNS if k not in UNTRANSLATED_COLS]
                               + [x for m in MODELS for x in m[3:]])
        if missing:
            print(f'cases/{envs.division()}/{env_id}.html: {len(missing)} string(s) without a translation in scripts/i18n.py TR (shown in Japanese):')
            for s in missing:
                print('  ' + s)
        print(f'{env_id}: {len(rows)} cases, {sum(r["requests"] for r in rows)} measured requests, ~{hours:.0f} h estimated')
        for step, s in est.items():
            print(f'  Tier {step}: {s["total_h"]} h (requests {s["request_s"] / 3600:.1f} h, launches {s["launch_s"] / 3600:.1f} h)')
    write_index(summaries, out_root)
    print(f'pages: {os.path.relpath(out_root / "CASES.html", ROOT)} ({"published/ only" if a.published else "results/ and published/"})')


if __name__ == '__main__':
    main()
