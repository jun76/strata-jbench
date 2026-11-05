"""Expand the benchmark plan in docs/SCOUTING.md into one row per case, for each test environment (envs/<id>/env.json).

Per environment it writes plan/<division>/<env>/cases.jsonl and cases.csv (the case list the runner consumes) and
cases/<division>/<env>/ (the human view: Markdown and CSV read on GitHub), and cases/README.md lists the environments. The environment decides which models run, how large each model
is for its GPU memory and RAM (for the estimate only), whether the DFlash2 cases exist (the card must have DFlash2) and
the time estimate. Re-run after a benchmark run: results/<division>/<env>/<run-id>/cases/<case-id>/summary.json,
when present, fills each row's status, headline metrics and evidence links. The newest run-id wins.

    python3 -I scripts/build_cases.py              # every environment, results/ and published/ -> preview/ (not tracked)
    python3 -I scripts/build_cases.py --published  # published/ only -> cases/ (the committed lists)
    python3 -I scripts/build_cases.py --env <id>   # one environment's case list
"""
import os
import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from i18n import one, tr, untranslated  # noqa: E402
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
    # Unsloth Dynamic v3.1 (the repository re-published on 2026-11-04, Strata's setup.py UNSLOTH_V31_*; engine 0.1.57 or
    # later). UD-IQ4_XS-v31 is Strata's name for the new UD-IQ4_XS, another file from the one above.
    ('unsloth', 'UD-IQ1_M', 68.0, '元重みの量子化 (Unsloth v3.1)'),
    ('unsloth', 'UD-Q2_0', 70.5, '元重みの量子化 (Unsloth v3.1)'),
    ('unsloth', 'UD-IQ2_XS', 75.8, '元重みの量子化 (Unsloth v3.1)'),
    ('unsloth', 'UD-Q2_K_XL', 79.6, '元重みの量子化 (Unsloth v3.1)'),
    ('unsloth', 'UD-IQ3_XXS', 83.6, '元重みの量子化 (Unsloth v3.1)'),
    ('unsloth', 'UD-Q3_K_XL', 89.5, '元重みの量子化 (Unsloth v3.1)'),
    ('unsloth', 'UD-IQ4_XS-v31', 93.7, '元重みの量子化 (Unsloth v3.1)'),
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
    ('cpu-pin', 'pcore', 'P コアのみ', '--pool-cores <P コアの論理 CPU>', 'P コア 1 つにつき 1 論理 CPU（lscpu で2スレッドを持つコア）、CPU 0 はホストスレッド用に除く。実際の値は計測する PC の lscpu で決まり、起動の記録（launch.txt）に残る'),
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
# The case lists' column headings; the CSVs keep the keys.
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
    '1': ('全モデルの基礎速度（decode 5種 × temperature 3水準、prefill 4K / 32K / 128K）。decode は DFlash2 対応のモデルで DFlash2 でも測る',
          'base speed of every model (5 decode kinds × 3 temperatures, prefill 4K / 32K / 128K); decode also with DFlash2 on the models that have it',
          '所有模型的基础速度（decode 5 种 × temperature 3 档，prefill 4K / 32K / 128K）；支持 DFlash2 的模型的 decode 也用 DFlash2 测量'),
    '2': ('公式 standard-v1（thinking xhigh、temperature 1.0）をスイートごと3回',
          'the official standard-v1 (thinking xhigh, temperature 1.0), the whole suite 3 times',
          '官方 standard-v1（thinking xhigh，temperature 1.0），整个套件 3 次'),
    '3': ('推論エフォート none / high × 4問、ゲーム作成は high のみ（全モデル）',
          'reasoning effort none / high × 4 tasks, the game at high only (every model)',
          '推理 effort none / high × 4 题，游戏制作仅 high（所有模型）'),
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


# The case lists are Markdown and CSV, read with GitHub's viewer: one Markdown file per language (README.md is Japanese,
# README.en.md English, README.zh.md Chinese, as for the repository's README). cases/README*.md lists the environments;
# cases/<division>/<env>/README*.md is one environment (its Tiers, models and shared conditions), tier-<step>*.md its
# cases, and tier-<step>.csv every case of the Tier with its parameters and result. The charts are separate (scripts/build_results.py).
LANG_FILES = {'ja': '', 'en': '.en', 'zh': '.zh'}
LANG_NAMES = {'ja': '日本語', 'en': 'English', 'zh': '中文'}
CSV_RESULT = ['status', 'run_id', 'n', 'prefill_tps', 'decode_tps', 'ttft_ms', 'first_answer_ms', 'total_ms',
              'reasoning_tokens', 'accept_rate', 'correct', 'evidence']


def md(v):
    """A table cell: no pipes or line breaks."""
    return str(v).replace('|', '\\|').replace('\n', ' ')


def langs_line(stem):
    return ' · '.join(f'[{LANG_NAMES[x]}]({stem}{s}.md)' for x, s in LANG_FILES.items()) + '\n'


def result_md(r, lang):
    m = r.get('result') or {}
    L = one(lang)
    labels = [('prefill_tps', 'prefill'), ('decode_tps', 'decode'), ('ttft_ms', 'TTFT ms'),
              ('accept_rate', L('採用率', 'acceptance', '接受率')), ('reasoning_tokens', L('思考', 'thinking', '思考')),
              ('correct', L('正答', 'correct', '正确'))]
    return ' / '.join(f'{label} {m[k]}' for k, label in labels if m.get(k) is not None)


def model_versions(rows, env_id, published_only, up, lang):
    """Per model, the repository and commit its results were measured with, from each RUN_ID's models.json
    (scripts/model_files.py): one line per version, with the RUN_IDs that used it. Two versions of one model in one
    environment are marked, since the case list then mixes them."""
    L = one(lang)
    dirs = {d.name: d for d in envs.run_dirs(env_id, published_only)}
    used = {}
    for r in rows:
        if r.get('run_id') in dirs:
            used.setdefault((r['family'], r['model']), set()).add(r['run_id'])
    records = {}
    for run in {x for v in used.values() for x in v}:
        p = dirs[run] / 'models.json'
        records[run] = {(m['family'], m['model']): m for m in json.loads(p.read_text())['models']} if p.exists() else {}
    out = {}
    for key, runs in used.items():
        seen = {}
        for run in sorted(runs):   # a version: its (repository, commit) pairs and, unless verified, the state on disk
            m = records[run].get(key)
            v = (tuple((s['repo'], s['revision']) for s in m['sources']), m['state']) if m else None
            seen.setdefault(v, []).append(run)
        lines = []
        for v, rs in seen.items():
            links = ' + '.join(f'[{repo} @ `{rev[:7]}`](https://huggingface.co/{repo}/tree/{rev})'
                               for repo, rev in v[0]) if v else L('記録なし', 'not recorded', '无记录')
            state = f' **{v[1]}**' if v and v[1] != 'verified' else ''
            runs_ = ', '.join(f'[{x}]({up}{(dirs[x] / "models.json").relative_to(ROOT)})'
                              if (dirs[x] / 'models.json').exists() else x for x in rs)
            lines.append(f'{links}{state} ({runs_})')
        warn = f'**{L("版が混在", "versions mixed", "版本混杂")}**: ' if len(seen) > 1 else ''
        out[key] = warn + '<br>'.join(lines)
    return out


COMMON = {
    'ja': '''- どのケースも3回測る（seed 1 / 2 / 3）。Tier 0 の IQ3_S は起動しなおしを含めて9回。standard-v1 はスイート全体を3回実行する。
- 起動: 専用プロファイル・専用ポート、`--vision off --parallel 1 --tune skip --drafting mtp`、そのほかは Strata の既定（auto）。表の「起動オプションの差分」はこれとの差だけを書く。drafter を MTP に固定するのは、0.2.10 から Auto がモデルによって DFlash2 と MTP を選び分けるため（DFlash2 は Tier 1 の decode を対応する11モデルで測り直し、drafter なしは Tier 5 で測る）。
- 同じ「起動セッション」のケースは、エンジンを1回起動したまま続けて回す（Tier 1・2・3・4a の 128K は同じセッション）。実行順は記録する。
- sampling（temperature 以外）: top_p 0.95 / top_k 20 / min_p 0 / presence_penalty 0 / repetition_penalty 1.0 を毎回明示する（Tier 0 の作者条件だけ例外）。
- thinking は毎回明示する。指定しないと、Web 画面で共有された Chat 設定 → 起動 config の値で埋まるため（`serve/server.py` の effort_default）。
  - off（effort none）: `"reasoning_effort": "none"` と `"chat_template_kwargs": {"enable_thinking": false}`
  - on（effort high）: `"reasoning_effort": "xhigh"` と `"chat_template_kwargs": {"enable_thinking": true}`、`reasoning_budget_tokens` も明示（出力 cap の 3/4。cap ≥ 1,024 で budget を省くと Strata の answer_room が同じ値を自動で入れる）
  - standard-v1（Tier 2）は公式の指定（xhigh、budget 0）のまま。cap 2,048 の sanity では answer_room により思考が 1,536 で閉じられる点を記録する
  - 各セッションの最初に `GET /settings`（共有設定が空であること）と `GET /config` を保存し、prompt token 数で effort の文が入ったかを確かめる
- 各セッションの最初に warm-up を1回（回数には含めない）。prefix cache の再利用を避けるため各リクエストに固有 ID を入れる（Tier 4 の2問目以降は意図的に再利用する）。
- OOM・起動失敗・timeout・skip も結果として残す。
''',
    'en': '''- Every case is measured 3 times (seed 1 / 2 / 3). Tier 0's IQ3_S runs 9 times, relaunching in between. standard-v1 runs the whole suite 3 times.
- Launch: a dedicated profile and port, `--vision off --parallel 1 --tune skip --drafting mtp`, everything else at Strata's default (auto). The “launch options” column lists only the difference from this. The drafter is pinned to MTP because since 0.2.10 Auto picks DFlash2 for some models and MTP for others (DFlash2 is measured on Tier 1's decode cases for the 11 models that have it, no drafter in Tier 5).
- Cases in the same “launch session” run one after another on a single engine launch (the 128K cases of Tiers 1, 2, 3 and 4a share one session). The order is recorded.
- Sampling (besides temperature): top_p 0.95 / top_k 20 / min_p 0 / presence_penalty 0 / repetition_penalty 1.0, sent with every request (except Tier 0's author settings).
- Thinking is set explicitly every time. Left out, it is filled from the Chat settings shared by the web UI, then from the launch config (effort_default in `serve/server.py`).
  - off (effort none): `"reasoning_effort": "none"` and `"chat_template_kwargs": {"enable_thinking": false}`
  - on (effort high): `"reasoning_effort": "xhigh"` and `"chat_template_kwargs": {"enable_thinking": true}`, with `reasoning_budget_tokens` set too (3/4 of the output cap; with cap ≥ 1,024 and no budget, Strata's answer_room puts in the same value)
  - standard-v1 (Tier 2) keeps the official settings (xhigh, budget 0). For sanity at cap 2,048, answer_room closes the thinking at 1,536; this is recorded
  - At the start of each session, `GET /settings` (the shared settings must be empty) and `GET /config` are saved, and the prompt token count confirms the effort text was added
- One warm-up at the start of each session (not counted). Each request carries a unique ID so the prefix cache is not reused (Tier 4 reuses it on purpose from the second question).
- OOM, launch failures, timeouts and skips are kept as results too.
''',
    'zh': '''- 每个用例测 3 次（seed 1 / 2 / 3）。Tier 0 的 IQ3_S 含重新启动共 9 次。standard-v1 整个套件运行 3 次。
- 启动：专用 profile 和专用端口，`--vision off --parallel 1 --tune skip --drafting mtp`，其余为 Strata 默认（auto）。表中“启动选项”只写与此不同之处。将 drafter 固定为 MTP，是因为自 0.2.10 起 Auto 会按模型分别选择 DFlash2 或 MTP（DFlash2 在 Tier 1 的 decode 中对支持它的 11 个模型另行测量，不使用 drafter 在 Tier 5 中测量）。
- 同一“启动会话”的用例在一次引擎启动中连续运行（Tier 1、2、3、4a 的 128K 共用一个会话）。记录运行顺序。
- sampling（temperature 以外）：每次都显式指定 top_p 0.95 / top_k 20 / min_p 0 / presence_penalty 0 / repetition_penalty 1.0（仅 Tier 0 的作者条件例外）。
- thinking 每次都显式指定。不指定时，会依次用 Web 界面共享的 Chat 设置 → 启动 config 的值填充（`serve/server.py` 的 effort_default）。
  - off（effort none）：`"reasoning_effort": "none"` 和 `"chat_template_kwargs": {"enable_thinking": false}`
  - on（effort high）：`"reasoning_effort": "xhigh"` 和 `"chat_template_kwargs": {"enable_thinking": true}`，并显式指定 `reasoning_budget_tokens`（输出 cap 的 3/4；cap ≥ 1,024 且省略 budget 时，Strata 的 answer_room 会自动填入相同的值）
  - standard-v1（Tier 2）保持官方设置（xhigh，budget 0）。cap 2,048 的 sanity 中 answer_room 会在 1,536 处结束思考，这一点会记录下来
  - 每个会话开始时保存 `GET /settings`（共享设置应为空）和 `GET /config`，并用 prompt token 数确认 effort 的提示已加入
- 每个会话开始时做 1 次 warm-up（不计入次数）。每个请求带唯一 ID，以免复用 prefix cache（Tier 4 从第 2 题起有意复用）。
- OOM、启动失败、超时、skip 也作为结果保留。
''',
}
GAME_LAYOUT = {
    'ja': ('ゲーム作成ケースの成果物の置き場所',
           f'プロンプト「{GAME_PROMPT}」をそのまま送る（形式の指示は足さない）。出力の形がケースごとに違っても、必ず次の形に展開する。',
           '''<run-id>/cases/<case id>/artifact/
  response.md     最終回答の全文（thinking は requests.jsonl 側）
  files/          コードブロックから取り出したファイル（ファイル名が書かれていればその名前、なければ言語ごとの既定名）
  manifest.json   取り出したファイル、名前の決め方、形式（単体 HTML / 要サーバー / その他）、README の有無、起動方法
  screenshot.png  単体 HTML か静的サーバーで開けた場合のみ。headless ブラウザで撮る''',
           '3回分は `artifact/` の下に seed ごとのフォルダ（`seed-1/` など）で分ける。'),
    'en': ('Where the game cases\' results go',
           f'The prompt “{GAME_PROMPT}” (Japanese for “make a Minecraft-like 3D sandbox game”) is sent as is, with no format instructions. Whatever shape each answer takes, it is always unpacked like this:',
           '''<run-id>/cases/<case id>/artifact/
  response.md     the whole final answer (the thinking is in requests.jsonl)
  files/          files taken from the code blocks (named as the answer names them, else a default per language)
  manifest.json   the files, how they were named, the form (single HTML / needs a server / other), README or not, how to run it
  screenshot.png  only if it opens as a single HTML file or from a static server; taken with a headless browser''',
           'The 3 runs go in one folder per seed under `artifact/` (`seed-1/` and so on).'),
    'zh': ('游戏制作用例的成果存放位置',
           f'原样发送提示“{GAME_PROMPT}”（日语，意为“做一个类似 Minecraft 的 3D 沙盒游戏”），不附加格式要求。无论每个用例的输出形式如何，都按以下结构展开：',
           '''<run-id>/cases/<case id>/artifact/
  response.md     最终回答全文（thinking 在 requests.jsonl 中）
  files/          从代码块中取出的文件（写了文件名就用该名称，否则用各语言的默认名）
  manifest.json   取出的文件、命名方式、形式（单个 HTML / 需要服务器 / 其他）、有无 README、运行方法
  screenshot.png  仅当能以单个 HTML 或静态服务器打开时。用 headless 浏览器截图''',
           '3 次的结果在 `artifact/` 下按 seed 分文件夹（`seed-1/` 等）。'),
}
PREVIEW_NOTE = {
    'ja': '> **プレビュー:** 計測中・公開前（`results/`）の結果も含む。コミットする一覧は `scripts/publish.py` で `published/` に移した結果だけから作る。\n',
    'en': '> **Preview:** includes results still in `results/` (measuring, not published). The committed lists are built only from runs moved to `published/` by `scripts/publish.py`.\n',
    'zh': '> **预览：** 包含 `results/` 中尚在测量、未发布的结果。提交的一览只由 `scripts/publish.py` 移到 `published/` 的结果生成。\n',
}
# The columns of a Tier's table; every other parameter is in the Tier's CSV.
TIER_COLS = ['id', 'model', 'context_label', 'config', 'launch_opts', 'fixture', 'effort', 'temperature', 'concurrency',
             'input_tokens', 'output_cap', 'reps']


def heading(label, lang):
    return one(lang)(label, *HEADINGS[label]) if label in HEADINGS else label


def tier_file(step, lang):
    return f'tier-{step}{LANG_FILES[lang]}.md'


def evidence_md(r, up):
    """The case's folder (summary.json, requests, responses, artifact), named by its RUN_ID."""
    if not r.get('run_id'):
        return ''
    folder = next((x for x in r['evidence'] if x.endswith('summary.json')), None)
    return f'[{r["run_id"]}]({up}{folder.rsplit("/", 1)[0]}/)' if folder else r['run_id']


def write_md(rows, out, cfg, published_only=False):
    """cases/<division>/<env>/ (or preview/cases/...): README*.md, tier-<step>*.md and tier-<step>.csv. Links to the result
    files are relative, so they also work at the tag a publish leaves (scripts/publish.py)."""
    up = os.path.relpath(ROOT, out) + '/'
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob('*.md'):
        old.unlink()
    est = estimate(rows)
    sessions = {}
    for r in rows:
        sessions[r['session']] = max(sessions.get(r['session'], 0), r['restarts'])
    total_h = sum(s['total_h'] for s in est.values())
    steps = list(dict.fromkeys(r['step'] for r in rows))
    division = envs.load_division(envs.division())
    for lang, suffix in LANG_FILES.items():
        L = one(lang)
        versions = model_versions(rows, cfg['id'], published_only, up, lang)
        done = sum(r['status'] == 'done' for r in rows)
        failed = sum(r['status'] in ('failed', 'unreadable') for r in rows)
        text = [langs_line('README'), f'[{L("← 環境の一覧", "← all environments", "← 环境一览")}]({os.path.relpath(out.parents[1], out)}/README{suffix}.md)\n',
                f'# {L("Strata ベンチ ケース一覧", "Strata bench cases", "Strata 基准测试 用例一览")}: {envs.label(cfg)}\n']
        if not published_only:
            text.append(PREVIEW_NOTE[lang])
        text.append(f'**{L("部門", "Division", "部门")}: {division["label"][lang]}** — {division["summary"][lang]} '
                    f'[{L("部門の一覧（エージェント部門は予定）", "All divisions (the agentic ones are planned)", "部门一览（智能体部门在计划中）")}]({up}divisions/README{suffix if (ROOT / f"divisions/README{suffix}.md").exists() else ""}.md)\n')
        text.append(L('Tier ごとにケースの表がある（1行が1ケース）。全パラメータと結果は Tier ごとの CSV（tier-<Tier>.csv）。'
                      'エビデンス列の RUN_ID は、そのケースの記録（summary.json、送ったリクエスト、応答、成果物）のフォルダ。'
                      f'生成: `scripts/build_cases.py`。',
                      'One table of cases per Tier (a row per case). Every parameter and result: the CSV of each Tier (tier-<Tier>.csv). '
                      'The RUN_ID in the evidence column opens the case\'s record (summary.json, the requests sent, the responses, the artifacts). '
                      'Generated by `scripts/build_cases.py`.',
                      '每个 Tier 一张用例表（每行一个用例）。全部参数与结果见各 Tier 的 CSV（tier-<Tier>.csv）。'
                      '证据列中的 RUN_ID 打开该用例的记录（summary.json、发送的请求、响应、成果物）。由 `scripts/build_cases.py` 生成。') + '\n')
        text.append(f'## {L("実行環境", "Test system", "运行环境")}\n\n' + machine_info.env_md(ROOT, cfg, lang, published_only))
        text.append(f'## {L("概要", "Overview", "概要")}\n')
        text.append(''.join(f'- {k}: {v}\n' for k, v in [
            (L('ケース', 'cases', '用例'), f'{len(rows):,}'),
            (L('本計測リクエスト', 'measured requests', '正式测量请求'), f'{sum(r["requests"] for r in rows):,}'),
            (L('エンジン起動', 'engine launches', '引擎启动'), f'{sum(sessions.values()):,}'),
            (L('見積もり', 'estimate', '预估'), f'{total_h:.0f} ' + L('時間', 'h', '小时')),
            (L('完了', 'done', '完成'), f'{done:,}'), (L('失敗', 'failed', '失败'), f'{failed:,}')]))
        text.append(f'\n## {L("Tier ごとの内訳", "By Tier", "各 Tier 明细")}\n')
        text.append(f'| Tier | {L("内容", "what", "内容")} | {L("モデル", "models", "模型")} | {L("ケース", "cases", "用例")} | '
                    f'{L("リクエスト", "requests", "请求")} | {L("見積 h", "est. h", "预估 h")} | {L("完了", "done", "完成")} |\n'
                    '| --- | --- | ---: | ---: | ---: | ---: | ---: |\n')
        tier_rows = []
        for step in steps:
            lst = [r for r in rows if r['step'] == step]
            info = L(*TIER_INFO[step]) if step in TIER_INFO else ''
            tier_rows.append(f'| [{step}]({tier_file(step, lang)}) | {md(info)} | {len({(r["family"], r["model"]) for r in lst})} | '
                             f'{len(lst):,} | {sum(r["reps"] for r in lst):,} | {est[step]["total_h"]} | '
                             f'{sum(r["status"] == "done" for r in lst)} |\n')
        text[-1] += ''.join(tier_rows)
        text.append(f'\n## {L("モデル", "Models", "模型")}\n\n'
                    f'| family | model | GB | {L("種別", "kind", "类别")} | '
                    f'{L("測った版（リポジトリ @ コミット、RUN_ID の models.json）", "version measured (repository @ commit, the RUN_ID's models.json)", "测量的版本（仓库 @ 提交，RUN_ID 的 models.json）")} |\n'
                    '| --- | --- | ---: | --- | --- |\n')
        text[-1] += ''.join(f'| {f} | {m} | {gb} | {md(tr(role, lang))} | {versions.get((f, m), "–")} |\n'
                            for f, m, gb, role in env_models())
        text.append(f'\n## {L("全ケース共通の条件", "Conditions shared by every case", "所有用例的共同条件")}\n\n{COMMON[lang]}')
        title, intro, tree, after = GAME_LAYOUT[lang]
        text.append(f'\n<details><summary>{title}</summary>\n\n{intro}\n\n```\n{tree}\n```\n\n{after}\n\n</details>\n')
        text.append(f'\n<details><summary>{L("見積もりの前提（rtx5090-128g の初回の計測の中央値。ほかの環境は env.json の assume で上書き）", "What the estimate assumes (medians of the first run on rtx5090-128g; other environments override them in env.json \"assume\")", "预估的前提（rtx5090-128g 首次测量的中位数；其他环境在 env.json 的 assume 中覆盖）")}</summary>\n\n'
                    f'```json\n{json.dumps(ASSUME, ensure_ascii=False, indent=2)}\n```\n\n</details>\n')
        (out / f'README{suffix}.md').write_text('\n'.join(text))

        for step in steps:
            lst = [r for r in rows if r['step'] == step]
            labels = dict(COLUMNS)
            head = ([L('状態', 'status', '状态')] + [heading(labels.get(k, k), lang) for k in TIER_COLS]
                    + [L('結果', 'result', '结果'), L('エビデンス', 'evidence', '证据')])
            body = []
            for r in lst:
                cells = []
                for k in TIER_COLS:
                    if k == 'id':
                        cells.append(f'`{r["id"]}`')
                    elif k == 'model':
                        cells.append(f'{r["family"]} {r["model"]}')
                    elif k == 'context_label':
                        cells.append(r['context_label'] + (f' (YaRN {r["yarn"]})' if r.get('yarn') else ''))
                    else:
                        cells.append(md(tr(cell(r[k], k), lang)))
                body.append('| ' + ' | '.join([r['status']] + cells + [md(result_md(r, lang)), evidence_md(r, up)]) + ' |')
            info = L(*TIER_INFO[step]) if step in TIER_INFO else ''
            page = [langs_line(f'tier-{step}'), f'[{L("← ケース一覧", "← cases", "← 用例一览")}](README{suffix}.md)\n',
                    f'# Tier {step}: {info}\n', f'{envs.label(cfg)} · ' + L(
                        f'{len(lst):,} ケース / {sum(r["reps"] for r in lst):,} リクエスト。ほかのパラメータ（入力の内容、見るもの、備考、seed、timeout、起動セッション）は [tier-{step}.csv](tier-{step}.csv)。',
                        f'{len(lst):,} cases / {sum(r["reps"] for r in lst):,} requests. The other parameters (input, measures, notes, seeds, timeout, launch session) are in [tier-{step}.csv](tier-{step}.csv).',
                        f'{len(lst):,} 个用例 / {sum(r["reps"] for r in lst):,} 个请求。其他参数（输入内容、测量内容、备注、seed、timeout、启动会话）见 [tier-{step}.csv](tier-{step}.csv)。') + '\n',
                    '| ' + ' | '.join(head) + ' |', '| ' + ' | '.join(['---'] * len(head)) + ' |', *body, '']
            (out / tier_file(step, lang)).write_text('\n'.join(page))

    for old in out.glob('*.csv'):
        old.unlink()
    for step in steps:   # one CSV per Tier: GitHub shows a CSV as a table only up to 512 KB
        with (out / f'tier-{step}.csv').open('w', newline='') as f:
            w = csv.writer(f)
            w.writerow([k for k, _ in COLUMNS] + CSV_RESULT)
            for r in rows:
                if r['step'] != step:
                    continue
                res = r.get('result') or {}
                folder = next((x for x in r['evidence'] if x.endswith('summary.json')), '')
                extra = {'status': r['status'], 'run_id': r.get('run_id', ''), 'evidence': folder.rsplit('/', 1)[0] + '/' if folder else ''}
                w.writerow([r[k] for k, _ in COLUMNS] + [extra[k] if k in extra else res.get(k, '') for k in CSV_RESULT])


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


def write_index(summaries, out_root, published_only):
    """cases/README*.md: the environments, each with its plan's size and progress, linking to its case list."""
    out = out_root / 'cases'
    out.mkdir(parents=True, exist_ok=True)
    division = envs.load_division(envs.division())
    for lang, suffix in LANG_FILES.items():
        L = one(lang)
        text = [langs_line('README'), f'# {L("Strata ベンチ ケース一覧", "Strata bench cases", "Strata 基准测试 用例一览")}\n']
        if not published_only:
            text.append(PREVIEW_NOTE[lang])
        text.append(L('ベンチを回すハードウェア構成（GPU と RAM の組み合わせ）ごとに、計画と結果を分けて持つ。環境の名前を開くと、その環境の全ケースの一覧。',
                      'The plan and the results are kept per hardware set-up (a GPU and an amount of RAM). Open an environment for all its cases.',
                      '按运行基准测试的硬件配置（GPU 与 RAM 的组合）分别保存计划和结果。点开环境名称即可查看该环境的全部用例。') + '\n')
        text.append(f'**{L("部門", "Division", "部门")}: {division["label"][lang]}** — {division["summary"][lang]}\n')
        text.append(f'| {L("環境", "environment", "环境")} | id | {L("ケース", "cases", "用例")} | {L("見積 h", "est. h", "预估 h")} | '
                    f'{L("完了", "done", "完成")} | {L("失敗", "failed", "失败")} |\n| --- | --- | ---: | ---: | ---: | ---: |')
        text += [f'| [{x["label"]}]({envs.division()}/{x["id"]}/README{suffix}.md) | `{x["id"]}` | {x["cases"]:,} | {x["hours"]:.0f} | '
                 f'{x["done"]:,} | {x["failed"]:,} |' for x in summaries]
        (out / f'README{suffix}.md').write_text('\n'.join(text) + '\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--env', default='', help='only this environment (default: every one in envs/)')
    ap.add_argument('--published', action='store_true',
                    help='only the runs in published/, written to cases/ (default: also results/, to preview/cases/)')
    a = ap.parse_args()
    out_root = ROOT if a.published else envs.PREVIEW
    summaries = []
    for env_id in envs.ids():
        cfg = envs.load(env_id)
        rows = build(cfg)
        attach_results(rows, env_id, a.published)
        est = estimate(rows)
        hours = sum(s['total_h'] for s in est.values())
        summaries.append({'id': env_id, 'label': envs.label(cfg), 'cases': len(rows), 'hours': hours,
                          'done': sum(r['status'] == 'done' for r in rows),
                          'failed': sum(r['status'] in ('failed', 'unreadable') for r in rows)})
        if a.env and env_id != a.env:
            continue
        write_plan(rows, env_id)
        write_md(rows, out_root / 'cases' / envs.division() / env_id, cfg, a.published)
        missing = untranslated([r[k] for r in rows for k, _ in COLUMNS if k not in UNTRANSLATED_COLS]
                               + [x for m in MODELS for x in m[3:]])
        if missing:
            print(f'cases/{envs.division()}/{env_id}/: {len(missing)} string(s) without a translation in scripts/i18n.py TR (shown in Japanese):')
            for s in missing:
                print('  ' + s)
        print(f'{env_id}: {len(rows)} cases, {sum(r["requests"] for r in rows)} measured requests, ~{hours:.0f} h estimated')
        for step, s in est.items():
            print(f'  Tier {step}: {s["total_h"]} h (requests {s["request_s"] / 3600:.1f} h, launches {s["launch_s"] / 3600:.1f} h)')
    write_index(summaries, out_root, a.published)
    print(f'case lists: {os.path.relpath(out_root / "cases", ROOT)}/ ({"published/ only" if a.published else "results/ and published/"})')


if __name__ == '__main__':
    main()
