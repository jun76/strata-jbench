"""The plan: the benchmark's cases, one row per case, for one test environment (envs/<id>/env.json).

What can be measured is the catalog (catalog/, scripts/catalog.py): the models and what holds for each base model. This
module expands it into cases (build, harness_build), says which models an environment measures and which stand for the
lineup (use_env, env_models, representatives), estimates the time (estimate) and attaches the results found in
results/ and published/ to the rows (attach_results). The environment decides which models run, how large each model
is for its GPU memory and RAM (for the estimate only) and whether the DFlash2 cases exist (the card must have DFlash2).

scripts/build_cases.py writes the plan and the case lists from these rows; the runner reads the plan it wrote.
"""
import os
import re
import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from i18n import one, tr, untranslated  # noqa: E402
import envs  # noqa: E402
import catalog  # noqa: E402
import engines  # noqa: E402
import machine_info  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

# (family, model, size GB, role), from the catalog (catalog/models/<base>.json; scripts/catalog.py). How large a model
# is for the environment's memory: size_class() (for the estimates).
CATALOG = catalog.load()
MODELS = catalog.builds(CATALOG)
_BASE = catalog.by_family(CATALOG)
_BUILD = {(e['family'], e['model']): e for b in CATALOG for e in b['builds']}


def display_model(family, model):
    """The model's name on the pages: the build's "display" where its name alone would mislead ('UD-Q2_K_XL (v3.1)',
    'UD-IQ4_XS (v3.1)' for UD-IQ4_XS-v31, 'UD-Q4_K_XL (pre-v3.1)' for a set the Hub replaced under the same name), else
    the name as it is. Case ids and folders keep the plain names."""
    return _BUILD.get((family, model), {}).get('display') or model


# A build that is not a quantization of the original weights (a fine-tune, a pruned version): "derivative" in the catalog
DERIVATIVE = {k for k, e in _BUILD.items() if e.get('derivative')}
# The engines that run a build (catalog "engines"; Strata where it says nothing), and the engine a plan is being built
# for: a build in another engine's format is that engine's alone (Sync-Strata's Sync-XS / S / M).
ENGINES_OF = {k: e.get('engines') or [engines.DEFAULT] for k, e in _BUILD.items()}
ENGINE = engines.DEFAULT
# The environment's reference model and the representatives of Tiers 4b, 4c and 5: set per environment by use_env, from
# env.json "ref" or Strata's own pick for its RAM + VRAM (envs.ref), and from roles (representatives()), never from a
# lineup named here, so that any card and any set of models gets a plan.
REF = None
TIER4B = TIER4C = TIER5 = []

K = 1024
CTX_LABEL = {32 * K: '32K', 64 * K: '64K', 128 * K: '128K', 200 * K: '200K', 256 * K: '256K',
             384 * K: '384K', 512 * K: '512K', 768 * K: '768K', 1024 * K: '1M'}
TRAINED = 256 * K
# What follows is each family's base model, as the catalog says it ("trained_context", "max_context", "thinking",
# "lineup", "drafter"); the plan below asks these, never a family's name.
# The trained length (past it Strata uses YaRN): Hy4-Flash reads 1M without it.
TRAINED_OF = {f: b['trained_context'] for f, b in _BASE.items()}
# The longest context a family's engine takes (Strata's inkling_fit.CONTEXTS ends at 256K); longer cases are not made.
MAX_CONTEXT_OF = {f: b['max_context'] for f, b in _BASE.items() if b['max_context']}
# Families served with thinking off only (Strata's inkling_family.HAS_THINKING False): their thinking-on cases are not
# made, and the coding task is asked with thinking off.
NO_THINKING = {f for f, b in _BASE.items() if not b['thinking']}
# Families that are another model than the lineup's main one (representatives: not the lineup's largest or smallest)
OTHER_MODELS = {f for f, b in _BASE.items() if b['lineup'] == 'other'}
# Families with a drafter of their own instead of the MTP layer the runner pins (bench_runner.launch_args): Hy4-Flash
# starts with DFly2, built into its builds (Strata's default for it); Tier 5's "--drafting off" still turns it off.
OWN_DRAFTER = {f: b['drafter']['label'] for f, b in _BASE.items() if 'builtin' in b['drafter']}
# Families whose engine reports no draft counts in the response's timings (strata-hy4 0.1.64 sends draft_n 0 while
# DFly2 runs; its log has only tree statistics), so no acceptance rate is measured for them.
NO_DRAFT_COUNTS = {f for f, b in _BASE.items() if b['drafter'].get('reports_counts') is False}


def drafter_measures(fam):
    return 'decode tok/s' if fam in NO_DRAFT_COUNTS else 'decode tok/s, MTP 採用率'

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

# Tier 5's VRAM reserve as a share of the card's VRAM (env.json hardware.gpu_vram_gib), the same rule in every
# environment: a fixed MiB means little on a 12 GB card and nothing on a 32 GB one. vram_reserve_mib() turns it into MiB.
VRAM_RESERVE_PCT = [10, 20, 30, 40, 50]
VRAM_RESERVE_NOTE = 'カードの VRAM（env.json の gpu_vram_gib）に対する割合。MiB に直した値を渡す（切り捨て）。足りずに起動できない割合もそのまま結果になる'

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
    *[('vram-reserve', f'{pct}pct', f'{pct}%', f'--set vram-reserve-mib=<VRAM の {pct}%>', VRAM_RESERVE_NOTE)
      for pct in VRAM_RESERVE_PCT],
    ('vision', 'gpu', 'gpu', '--vision gpu', '画像は入れない。エンコーダが VRAM を取る分の損失だけを見る'),
    ('pool-workers', '8', '8', '--set pool-workers=8', ''),
    ('cpu-pin', 'pcore', 'P コアのみ', '--pool-cores <P コアの論理 CPU>', 'P コア 1 つにつき 1 論理 CPU（P コアはカーネルの cpu_core の一覧、それが無ければ lscpu で2スレッドを持つコア）、CPU 0 はホストスレッド用に除く。実際の値は計測する PC で決まり、起動の記録（launch.txt）に残る'),
    ('ple-io', 'mmap', 'mmap', '--set ple-io=mmap', ''),
    ('parallel', '2', '2', '--parallel 2', 'クライアント並列数も 2'),
    ('parallel', '4', '4', '--parallel 4', 'クライアント並列数も 4'),
    ('tune', 'quick', 'quick', '--tune quick --retune', 'tuner の所要時間も記録'),
    ('tune', 'thorough', 'thorough', '--tune thorough --retune', 'tuner の所要時間も記録'),
]
TIER5_CASES = ['decode-prose-ja', 'decode-code', 'prefill-4k', 'prefill-32k']
# Families whose models DFlash2 drafts (strata launch --plan on 0.1.56 and 0.1.58: Auto picks it for these; coder, swift and nvfp4
# stay on MTP). Every case pins MTP; only these models also get Tier 1's decode cases with DFlash2.
DFLASH2_FAMILIES = {f for b in CATALOG for f in b['drafter'].get('also', {}).get('dflash2', [])}
DFLASH2_NOTE = '0.2.10 から Auto はこのモデルで DFlash2 を選ぶ（ほかのケースは MTP に固定）。drafter（1.2 GB。0.2.12 から一部のモデルは Strata が調整した 0.34 GB も）は計測前に取得しておく'

# Practical coding cases. Plain Tiers 0 and 3 ask for a scene titled "A sailing ship calling at a harbor" in 3D voxel art as
# one HTML file; the Minecraft prompt, sent verbatim with no format instructions, is the harness divisions' case
# (docs: divisions/README.md).
GAME_FIXTURE = 'coding-harbor'
GAME_PROMPT = ('Create a 3D voxel art scene: "A sailing ship calling at a harbor". The scene should render immediately and be '
               'viewable with the mouse. … make sure I can paste it all into a single HTML file and open it in Chrome.')
# The coding cap: the whole 128K window but the prompt (about 100 tokens) and a margin; thinking is 64K
# (bench_runner.CODING_THINKING): every model thinks all of its budget on this task, and the page has the other 63K.
CODING_CAP = 128 * K - 1024
CODING_THINKING = 65536
# The harness divisions' game: thinking fixed at 32K (bench_runner.HARNESS_THINKING) and the same whole-window cap,
# which the engine shortens on every request to what the prompt leaves of the context (fit_max_tokens): a harness case
# is meant to finish, and only the time limit stops one that loops.
HARNESS_THINKING = 32768
GAME_NOTE = ('成果物は artifact/ に展開（response.md、files/、manifest.json、静的 HTML なら screenshot.png）。'
             '単一の HTML ファイルか、形式（単体 HTML / 要サーバー / README の有無）は manifest に記録')
HARNESS_FIXTURE = 'game-minecraft'
HARNESS_PROMPT = 'マイクラ風3D箱庭ゲーム作って'
HARNESS_NOTE = ('ハーネスに one shot で渡す（形式の指示なし）。成果物は作業ディレクトリに書かれた HTML、なければ回答のコードブロックから '
                'artifact/ に展開。sampling・thinking・seed・出力 cap は記録プロキシがリクエストごとに入れる')

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
    # the coding task: every model thinks all of its budget (64K at high); pages ran to 5K-40K
    'game_reasoning_tokens': {'none': 0, 'low': 3000, 'medium': 6000, 'high': 66000},
    'game_answer_tokens': 20000,
    'task_answer_tokens': 550,
    'long_answer_tokens': 150,
    'sanity_output_tokens': 150,
    'standard_runs': 3,                 # Tier 2: the suite runs 3 times, each on its own engine
    'long_cached_tokens': 16384,        # Tiers 4b-4d: what a later question reuses of the document (one checkpoint)
    'standard_run_overhead_s': 60,      # per run, on top of the launch: the suite's own warm-up and checks
}


def yarn(ctx, fam=None):
    trained = TRAINED_OF.get(fam, TRAINED)
    return f'{ctx / trained:g}' if ctx > trained else ''


def base(tier, step, fam, model, **kw):
    row = dict(tier=tier, step=step, family=fam, model=model, context=128 * K, yarn='',
               launch_opts='', config='baseline', fixture='', content='', input_tokens='',
               output_cap='', effort='none', temperature=0.7, concurrency=1, reps=3,
               seeds='1,2,3', timeout_s=1800, measures='', note='', restarts=1, artifact=False)
    row.update(kw)
    row['context_label'] = CTX_LABEL.get(row['context'], str(row['context']))
    if 'yarn' not in kw:
        row['yarn'] = yarn(row['context'], fam)
    row['id'] = '-'.join(str(x) for x in [f"T{step}", fam, model, row.pop('_key')])
    return row


def thinking_budget(cap):
    """The budget Strata's answer_room would pick for this cap (serve/server.py), sent explicitly instead."""
    return cap - min(max(512, cap // 4), cap // 2)


def effort_note(effort, cap, coding=None):
    """coding: 'page' (plain's coding task: 64K) or 'game' (the harness divisions': 32K), as
    bench_runner.thinking_budget sends."""
    if effort == 'none':
        return 'thinking off: reasoning_effort "none" + chat_template_kwargs.enable_thinking false'
    budget = {'page': min(CODING_THINKING, cap), 'game': min(HARNESS_THINKING, cap)}.get(coding, thinking_budget(cap))
    why = {'page': '。コーディングは思考を 64K に固定し、cap はコンテキスト 128K の枠いっぱい: どのモデルも思考の予算を使い切るので、残りの約 63K をページに充てる）',
           'game': '。ハーネス部門は完走が前提: 思考を 32K に固定し、cap は窓いっぱい（各リクエストで文脈の残りに縮む）、止めるのは時間制限だけ）'}.get(coding, '）')
    return (f'thinking on: reasoning_effort "xhigh" + chat_template_kwargs.enable_thinking true、'
            f'reasoning_budget_tokens {budget:,}（明示' + why)


def game_case(tier, step, fam, model, effort, temperature, cap, timeout):
    return base(tier, step, fam, model, _key=f'{GAME_FIXTURE}-{effort}', fixture=GAME_FIXTURE,
                content='港に寄港する帆船の情景を 3D ボクセルアートの単一の HTML ファイルで（実用的なコーディング）', input_tokens='短文', output_cap=cap,
                effort=effort, temperature=temperature, timeout_s=timeout, artifact=True,
                measures='完了時間, 出力 token, cap 到達, 成果物が動くか',
                note=effort_note(effort, cap, coding='page') + '。' + GAME_NOTE)


def tier1_cases(tier, step, fam, model, **kw):
    rows = []
    for fx, content in DECODE:
        for t in TEMPS:
            rows.append(base(tier, step, fam, model, _key=f'{fx}-t{t:g}', fixture=fx, content=content,
                             input_tokens='短文', output_cap=512, temperature=t,
                             measures=drafter_measures(fam), **kw))
    for fx, n in PREFILL:
        rows.append(base(tier, step, fam, model, _key=fx, fixture=fx, content=PREFILL_CONTENT,
                         input_tokens=n, output_cap=128, measures='prefill tok/s, TTFT, 長文後の decode', **kw))
    return rows


def build(cfg):
    """Every case of the environment: each engine jbench starts itself (catalog/engines/, "managed") gets the cases of
    its own builds, limited to what the engine's entry allows ("steps", "max_context"); a row's "engine" says whose it
    is. An attach-only engine has no rows of its own: it borrows the plain ones (config.select)."""
    global ENGINE
    division = envs.load_division(envs.division())
    rows = []
    for e in engines.entries():
        if not e['managed'] or (division.get('harness') and e['id'] != engines.DEFAULT):
            continue
        ENGINE = e['id']
        part = _engine_rows(cfg, division)
        if e['id'] != engines.DEFAULT:
            # another engine takes none of Strata's launch options (the DFlash2 launches, Tier 5's variants)
            part = [r for r in part if not r['launch_opts']]
        part = [r for r in part if (not e.get('steps') or r['step'] in e['steps'])
                and (not e.get('max_context') or r['context'] <= e['max_context'])]
        for r in part:
            r['engine'] = e['id']
        rows += part
    ENGINE = engines.DEFAULT
    use_env(cfg)
    return finish(rows, cfg)


def _engine_rows(cfg, division):
    use_env(cfg)
    if division.get('harness'):
        return harness_build(division)
    names = {(f, m) for f, m, *_ in env_models()}
    rows = []
    # Tier 0: instrument check on the reference model across 3 engine restarts, plus the author's protocol on Gyro-S.
    for r in tier1_cases('0', '0', *REF) if REF else []:
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
    if REF:
        rows.append(game_case('0', '0', *REF, 'none', 0.7, CODING_CAP, 1800))
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
            for eff in ['none'] if fam in NO_THINKING else EFFORTS:
                rows.append(base('3', '3', fam, model, _key=f'{task}-{eff}', fixture=task, content=content,
                                 input_tokens='短文', output_cap=16384, effort=eff, temperature=1.0,
                                 measures='思考 token 数, 回答までの時間, 完了時間, 正答, cap 到達',
                                 note=effort_note(eff, 16384)))
        for eff in ['none'] if fam in NO_THINKING else GAME_EFFORTS:
            rows.append(game_case('3', '3', fam, model, eff, 1.0, CODING_CAP, 3600))

    for fam, model, *_ in env_models():
        for ctx in [c for c in [128 * K, 256 * K, 1024 * K] if c <= MAX_CONTEXT_OF.get(fam, c)]:
            rows.append(base('4', '4a', fam, model, _key=f'ctxcost-{CTX_LABEL[ctx]}', context=ctx,
                             fixture='ctxcost-4k', content='4K の文章 + 続きを書く指示', input_tokens=4 * K,
                             output_cap=512, measures='decode tok/s, expert cache スロット数, VRAM / RAM peak, 起動可否'))

    def long_rows(step, models, lengths, ctx_of, timeout):
        out = []
        for fam, model in models:
            for n, label in lengths:
                if ctx_of(n) > MAX_CONTEXT_OF.get(fam, ctx_of(n)):
                    continue
                for q, content in QUESTIONS:
                    first = q == QUESTIONS[0][0]
                    out.append(base('4', step, fam, model, _key=f'long-{label}-{q}', context=ctx_of(n),
                                    fixture=f'long-{label}', content=content, input_tokens=n, output_cap=512,
                                    timeout_s=timeout,
                                    measures=('prefill tok/s, TTFT, 長文後の decode, RAM / VRAM peak, 正答'
                                              if first else '正答（文書部分は prefix cache を使う）')))
        return out

    def tier4b(models):
        return long_rows('4b', models, [(32 * K, '32K'), (128 * K, '128K'), (TRAINED, '256K')], lambda n: TRAINED, 1800)

    def tier4c(models):
        return long_rows('4c', models, [(512 * K, '512K'), (1024 * K, '1M')], lambda n: n, 7200)

    def tier5(models):
        out = []
        for fam, model in models:
            for var, slug, level, opts, note in TIER5_VARIANTS:
                for fx in TIER5_CASES:
                    is_prefill = fx.startswith('prefill')
                    n = dict(PREFILL).get(fx, '短文')
                    conc = int(level) if var == 'parallel' else 1
                    out.append(base('5', '5', fam, model, _key=f'{var}-{slug}-{fx}',
                                    config=f'{var}={level}', launch_opts=vram_reserve_mib(opts, cfg), fixture=fx,
                                    content=PREFILL_CONTENT if is_prefill else dict(DECODE)[fx],
                                    input_tokens=n, output_cap=128 if is_prefill else 512, concurrency=conc,
                                    measures='prefill tok/s, TTFT' if is_prefill else drafter_measures(fam),
                                    note=note))
        return out

    rows += tier4b(TIER4B)
    rows += tier4c(TIER4C)
    for n, label, arms in [(300 * K, '300K', [(384 * K, 'yarn1.5', '', 'factor 1.5'),
                                              (384 * K, 'none', '--set rope-scaling=none', 'YaRN なし（学習長超え）')]),
                           (200 * K, '200K', [(256 * K, 'none', '', 'YaRN なし'),
                                              (1024 * K, 'yarn4', '', 'factor 4')])]:
        for ctx, arm_id, opts, arm in arms if REF else []:
            for q, content in QUESTIONS:
                extra = {'yarn': 'なし'} if arm_id == 'none' else {}
                rows.append(base('4', '4d', *REF, _key=f'yarn-{label}-ctx{CTX_LABEL[ctx]}-{arm_id}-{q}',
                                 context=ctx, launch_opts=opts, **extra, **({'config': 'rope-scaling=none'} if opts else {}), fixture=f'long-{label}', content=content, input_tokens=n,
                                 output_cap=512, timeout_s=7200, measures='正答, prefill / decode tok/s',
                                 note=arm + ('。rope の flag 名は engine の解決済み設定で確認する' if opts else '')))

    rows += tier5(TIER5)
    rows = [r for r in rows if (r['family'], r['model']) in names]   # Tiers 0, 4 and 5 name their models directly
    return rows




def representatives(models):
    """Tiers 4b, 4c and 5's models, chosen by role from the environment's models (derivatives left out unless there is
    nothing else), so that every card and lineup gets them: 4b the reference, the largest model of each family and the
    smallest model; 4c and 5 the reference, the largest and the smallest. Only the file sizes order them: how a model
    runs on the card is what is measured, not guessed here."""
    cand = [(f, m, gb) for f, m, gb, _ in models if (f, m) not in DERIVATIVE] or [(f, m, gb) for f, m, gb, _ in models]
    if not cand:
        return [], [], []
    # The largest and the smallest are Qwen3.8-Flash-Next's (the lineup the reference is from); another model (Hy4-Flash,
    # Inkling-2-Mini) is a representative only as its family's largest in 4b, unless nothing else is measured
    main = [x for x in cand if x[0] not in OTHER_MODELS] or cand
    largest = max(main, key=lambda x: x[2])[:2]
    smallest = min(main, key=lambda x: x[2])[:2]
    families = list(dict.fromkeys(f for f, _, _ in cand))
    per_family = [max((x for x in cand if x[0] == f), key=lambda x: x[2])[:2] for f in families]

    def uniq(xs):
        out = []
        for x in xs:
            if x and x not in out:
                out.append(x)
        return out
    return uniq([REF, *per_family, smallest]), uniq([REF, smallest, largest]), uniq([REF, largest, smallest])


def harness_build(division):
    """A harness division (divisions/<division>/division.json "harness"): the Minecraft game only, handed to the harness in
    one shot, on the division's models ("models": "family model", or "ref" for the environment's reference model) that this environment has, at the plain baseline's
    context (128K) and launch. The engine-side conditions (sampling, thinking, seed, cap) are those of plain Tier 3's game."""
    keep = [(' '.join(REF) if REF else None) if k == 'ref' else k for k in division.get('models') or []]
    if division.get('models') and not any(keep):
        return []   # only "ref", and this environment has none (use_env said why)
    rows = []
    for fam, model, *_ in env_models():
        if keep and f'{fam} {model}' not in keep:
            continue
        rows.append(base('G', 'G', fam, model, _key=f'{HARNESS_FIXTURE}-high', fixture=HARNESS_FIXTURE,
                         content=f'「{HARNESS_PROMPT}」（ハーネス越しの実用的なコーディング）', input_tokens='短文',
                         output_cap=CODING_CAP, effort='high', temperature=1.0, timeout_s=3600, artifact=True,
                         harness=division['harness'],
                         measures='完了時間, ターン数, tool call, ハーネスの前置き token, cached の割合, 成果物が動くか',
                         note=effort_note('high', CODING_CAP, coding='game') + '。' + HARNESS_NOTE))
    return rows


def finish(rows, cfg):
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


def vram_reserve_mib(opts, cfg):
    """'--set vram-reserve-mib=<VRAM の 20%>' -> '--set vram-reserve-mib=2437' for this environment's card."""
    m = re.search(r'<VRAM の (\d+)%>', opts)
    if not m:
        return opts
    gib = (cfg.get('hardware') or {}).get('gpu_vram_gib')
    if not gib:
        raise SystemExit(f"{cfg.get('id')}: env.json has no hardware.gpu_vram_gib, needed for Tier 5's VRAM reserve")
    return opts.replace(m.group(0), str(int(gib * 1024 * int(m.group(1)) / 100)))


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
    """The environment the plan is built for: its models, its estimate's assumptions, its reference model (envs.ref:
    env.json "ref", else Strata's own recommendation; the only grounds, so when the environment does not measure that
    model there is none until env.json names one, and Tiers 0 and 4d are left out) and the representatives."""
    global ENV, ASSUME_ENV, REF, TIER4B, TIER4C, TIER5
    ENV = cfg
    ASSUME_ENV = {**ASSUME, **(cfg.get('assume') or {})}
    models = env_models()
    want = tuple((envs.ref(cfg) or '').split()) or None
    if ENGINE != engines.DEFAULT:
        want = None      # the reference is Strata's recommendation: another engine has none
    elif want not in {(f, m) for f, m, *_ in models}:
        print(f'{cfg["id"]}: the reference model {" ".join(want) if want else "(none: no Strata source to ask)"} is not '
              'among the models this environment measures; Tiers 0 and 4d are left out until env.json "ref" names one of them',
              file=sys.stderr)
        want = None
    REF = want
    TIER4B, TIER4C, TIER5 = representatives(models)


def env_models():
    """The models this environment runs on the engine being planned: every build the catalog has for that engine, or
    the ones of them env.json lists."""
    keep = ENV.get('models') if ENV else None
    return [m for m in MODELS if ENGINE in ENGINES_OF[(m[0], m[1])] and (not keep or f'{m[0]} {m[1]}' in keep)]


def result_ids(env_id, published_only=False):
    """The case ids that have a result in this environment (published/, and results/ unless published_only)."""
    return {s.parent.name for run in envs.run_dirs(env_id, published_only) for s in run.glob('cases/*/summary.json')}


def measured_rows(cfg, plan, have):
    """The cases the pages keep beside the plan: a model this environment no longer measures (left out of env.json
    "models", say when its files were replaced or the disk was short) keeps its results on the pages and in the lists,
    as long as the plan builder still makes the same case for it. A case whose definition changed or left the builder
    (another prompt, another cap) leaves them, as AGENTS.md 2.1 says. plan: build(cfg); have: result_ids()."""
    if not cfg.get('models'):
        return []
    ids = {r['id'] for r in plan}
    rows = [r for r in build({**cfg, 'models': None}) if r['id'] in have and r['id'] not in ids]
    use_env(cfg)   # build() set the environment to every model
    return rows


def page_models(rows):
    """The models the pages list: this environment's, then the ones only its earlier results have, in MODELS order."""
    keep = {(f, m) for f, m, *_ in env_models()} | {(r['family'], r['model']) for r in rows}
    return [m for m in MODELS if (m[0], m[1]) in keep]


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
    if fx.startswith(('coding-', 'game-')):
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
    rows = [r for r in rows if not r.get('retired')]
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
