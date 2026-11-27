"""Write the plan and the case lists of each test environment (envs/<id>/env.json); the cases themselves are
scripts/case_plan.py, what can be measured is the catalog (catalog/).

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
import re
import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from i18n import one, tr, untranslated  # noqa: E402
import engines  # noqa: E402
import envs  # noqa: E402
import catalog  # noqa: E402
import machine_info  # noqa: E402

import case_plan  # noqa: E402
from case_plan import *  # noqa: E402,F401,F403  (the rows, the model table and the estimate; what use_env sets is read as case_plan.X)


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
    '0': ('計測器の検証（基準モデル × 起動3回、Gyro-S で作者の値と照合、コーディングの成果物の展開確認）',
          'validating the harness (the reference model × 3 launches, Gyro-S against the author\'s figures, unpacking the coding result)',
          '验证测量工具（基准模型 × 启动 3 次、用 Gyro-S 对照作者的数值、确认编程成果的展开）'),
    '1': ('全モデルの基礎速度（decode 5種 × temperature 3水準、prefill 4K / 32K / 128K）。decode は DFlash2 対応のモデルで DFlash2 でも測る',
          'base speed of every model (5 decode kinds × 3 temperatures, prefill 4K / 32K / 128K); decode also with DFlash2 on the models that have it',
          '所有模型的基础速度（decode 5 种 × temperature 3 档，prefill 4K / 32K / 128K）；支持 DFlash2 的模型的 decode 也用 DFlash2 测量'),
    '2': ('公式 standard-v1（thinking xhigh、temperature 1.0）をスイートごと3回',
          'the official standard-v1 (thinking xhigh, temperature 1.0), the whole suite 3 times',
          '官方 standard-v1（thinking xhigh，temperature 1.0），整个套件 3 次'),
    '3': ('推論エフォート none / high × 4問、コーディング（帆船）は high のみ（全モデル）',
          'reasoning effort none / high × 4 tasks, the coding task (sailing ship) at high only (every model)',
          '推理 effort none / high × 4 题，编程（帆船）仅 high（所有模型）'),
    'G': ('コーディング（マイクラ）をハーネスに one shot で渡す',
          'the coding task (Minecraft) handed to the harness in one shot',
          '把编程任务（Minecraft）一次性交给 harness'),
    '4a': ('容量の確保コスト（128K / 256K / 1M に同じ 4K 入力）',
           'the cost of reserving context (the same 4K input at 128K / 256K / 1M)',
           '预留上下文的代价（128K / 256K / 1M 下相同的 4K 输入）'),
    '4b': ('学習範囲の長文（32K / 128K / 256K。基準モデル、系列ごとに最大のモデル、最小のモデル）',
           'long inputs within the trained length (32K / 128K / 256K; the reference model, the largest of each family, the smallest)',
           '训练长度内的长文本（32K / 128K / 256K；基准模型、各系列最大的模型、最小的模型）'),
    '4c': ('拡張範囲の長文（512K / 1M。基準モデル、最小と最大のモデル）', 'long inputs in the extended range (512K / 1M; the reference model, the smallest and the largest)',
           '扩展范围的长文本（512K / 1M；基准模型、最小与最大的模型）'),
    '4d': ('YaRN の影響（基準モデル、同じ入力で設定だけ変える）', 'the effect of YaRN (the reference model, same input, only the setting changes)',
           'YaRN 的影响（基准模型，相同输入只改设置）'),
    '5': ('起動オプションを1つずつ変える（基準モデル、最大と最小のモデル。自動 tune を含む）', 'changing one launch option at a time (the reference model, the largest and the smallest; auto tune included)',
          '每次只改一个启动选项（基准模型、最大与最小的模型；含自动 tune）'),
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
    'ja': '''- どのケースも3回測る（seed 1 / 2 / 3）。Tier 0 の基準モデルは起動しなおしを含めて9回。standard-v1 はスイート全体を3回実行する。
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
    'en': '''- Every case is measured 3 times (seed 1 / 2 / 3). Tier 0's reference model runs 9 times, relaunching in between. standard-v1 runs the whole suite 3 times.
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
    'zh': '''- 每个用例测 3 次（seed 1 / 2 / 3）。Tier 0 的基准模型含重新启动共 9 次。standard-v1 整个套件运行 3 次。
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
    'ja': ('コーディングのケースの成果物の置き場所',
           'Tier 0・3 のコーディングは「港に寄港する帆船」の情景（英文のプロンプトで、情景は題だけを示し、3D ボクセルアートで、単一の HTML ファイルで答えるよう指定する。全文は prompts/coding-harbor.json）。出力の形がケースごとに違っても、必ず次の形に展開する。',
           '''<run-id>/cases/<case id>/artifact/
  response.md     最終回答の全文（thinking は requests.jsonl 側）
  files/          コードブロックから取り出したファイル（ファイル名が書かれていればその名前、なければ言語ごとの既定名）
  manifest.json   取り出したファイル、名前の決め方、形式（単体 HTML / 要サーバー / その他）、README の有無、起動方法
  screenshot.png  単体 HTML か静的サーバーで開けた場合のみ。headless Chrome でページを 10 秒動かしてから撮る
  console.txt     そのときのエラー（捕まえられなかった例外、console.error、読み込みの失敗）。manifest の screenshot に、描画されたか（ほぼ一色・輪郭なしなら空白）と、固まったか（読み込みが CDN で止まっただけなら「読み込み待ち」）も残る''',
           '3回分は `artifact/` の下に seed ごとのフォルダ（`seed-1/` など）で分ける。'),
    'en': ('Where the coding cases\' results go',
           'The coding task of Tiers 0 and 3 is a scene titled "A sailing ship calling at a harbor" (an English prompt that gives the scene by its title alone and asks for it in 3D voxel art, as one HTML file; the whole text is in prompts/coding-harbor.json). Whatever shape each answer takes, it is always unpacked like this:',
           '''<run-id>/cases/<case id>/artifact/
  response.md     the whole final answer (the thinking is in requests.jsonl)
  files/          files taken from the code blocks (named as the answer names them, else a default per language)
  manifest.json   the files, how they were named, the form (single HTML / needs a server / other), README or not, how to run it
  screenshot.png  only if it opens as a single HTML file or from a static server; taken after the page has run 10 s in headless Chrome
  console.txt     its errors then (uncaught exceptions, console.error, failed loads); the manifest's screenshot also says whether anything was drawn (nearly one colour or no edges: empty) and whether the page froze (or only stalled on a CDN)''',
           'The 3 runs go in one folder per seed under `artifact/` (`seed-1/` and so on).'),
    'zh': ('编程用例的成果存放位置',
           'Tier 0、3 的编程任务是“帆船停靠港口”的场景（英文提示，场景只给出标题，要求以 3D 体素艺术、用单个 HTML 文件回答；全文见 prompts/coding-harbor.json）。无论每个用例的输出形式如何，都按以下结构展开：',
           '''<run-id>/cases/<case id>/artifact/
  response.md     最终回答全文（thinking 在 requests.jsonl 中）
  files/          从代码块中取出的文件（写了文件名就用该名称，否则用各语言的默认名）
  manifest.json   取出的文件、命名方式、形式（单个 HTML / 需要服务器 / 其他）、有无 README、运行方法
  screenshot.png  仅当能以单个 HTML 或静态服务器打开时。在 headless Chrome 中让页面运行 10 秒后截图
  console.txt     当时的错误（未捕获的异常、console.error、加载失败）；manifest 的 screenshot 还记录是否画出了内容（几乎一种颜色或没有轮廓则为空白）以及页面是否卡死''',
           '3 次的结果在 `artifact/` 下按 seed 分文件夹（`seed-1/` 等）。'),
}
# A harness division's shared conditions and where its game's results go (divisions/<division>/division.json "harness").
HARNESS_COMMON = {
    'ja': '''- ケースはコーディング（マイクラ、「マイクラ風3D箱庭ゲーム作って」）だけ。形式の指示を足さずに、ハーネスに one shot で渡す（非対話、プロンプトは stdin かファイル）。各3回（seed 1 / 2 / 3）。
- エンジンの起動はプレーンの基準と同じ: コンテキスト 128K、`--vision off --parallel 1 --tune skip --drafting mtp`。
- ハーネスはエンジンに直接つながず、ランナーの記録プロキシを通す。プロキシは各リクエストの sampling（temperature 1.0、top_p 0.95 / top_k 20 / min_p 0 / presence_penalty 0 / repetition_penalty 1.0）、thinking（xhigh、思考の上限 32,768）、seed、出力 cap 130,048（窓いっぱい。エンジンが各リクエストで文脈の残りに縮める）をケースの値にそろえ、ハーネスが送った元の値は記録する。ハーネスの差だけが残るようにするため（送らない項目は Strata が共有の Chat 設定や model card で埋めるので、ハーネスごとに条件がずれる）。
- ハーネスの設定は、版を固定し、ユーザーの設定とは分けたディレクトリに作る。窓 131,072 / 出力上限 32,768。自動の compaction と、タイトル生成などの副次リクエストは切る（切れないものは記録して本筋と分けて数える）。tool は作業ディレクトリの中では承認なしで実行し、閉じ込めは外側（bubblewrap）で行う。
- 作業ディレクトリはケースと seed ごとの使い捨て。測るのは完了までの壁時計、その内訳（ハーネスの起動、ターン数、tool call、ハーネスの前置きの token、prefix cache の再利用）と成果物。
''',
    'en': '''- The only case is the coding task (Minecraft, “マイクラ風3D箱庭ゲーム作って”), handed to the harness in one shot with no format instructions (non-interactive, the prompt on stdin or in a file). 3 runs each (seed 1 / 2 / 3).
- The engine is launched as for plain's baseline: context 128K, `--vision off --parallel 1 --tune skip --drafting mtp`.
- The harness does not talk to the engine directly but through the runner's recording proxy. The proxy sets each request's sampling (temperature 1.0, top_p 0.95 / top_k 20 / min_p 0 / presence_penalty 0 / repetition_penalty 1.0), thinking (xhigh, a thinking budget of 32,768), seed and output cap 130,048 (the whole window, which the engine shortens on every request to what the context has left) to the case's values and records what the harness sent, so that only the harness differs (what a harness leaves out, Strata fills in from the shared Chat settings or the model card, which would differ per harness).
- Each harness is pinned to a version and configured in a folder of its own, apart from the user's settings: window 131,072 / output limit 32,768. Automatic compaction and side requests such as title generation are off (any that cannot be turned off are recorded and counted apart). Tools run without approval inside the work folder, confined from outside (bubblewrap).
- A fresh work folder per case and seed. Measured: the wall-clock time to the end, what it is made of (the harness's start, turns, tool calls, the tokens of the harness's own preamble, prefix-cache reuse) and the result.
''',
    'zh': '''- 用例只有编程任务（Minecraft，“マイクラ風3D箱庭ゲーム作って”），不附加格式要求，一次性交给 harness（非交互，提示经 stdin 或文件传入）。各 3 次（seed 1 / 2 / 3）。
- 引擎启动与纯模型的基准相同：上下文 128K，`--vision off --parallel 1 --tune skip --drafting mtp`。
- harness 不直接连接引擎，而是经过 runner 的记录代理。代理把每个请求的 sampling（temperature 1.0，top_p 0.95 / top_k 20 / min_p 0 / presence_penalty 0 / repetition_penalty 1.0）、thinking（xhigh，思考上限 32,768）、seed、输出 cap 130,048（整个窗口，引擎在每个请求中缩短为上下文剩余的部分）统一为用例的值，并记录 harness 原本发送的值，使差异只来自 harness（harness 不发送的项目由 Strata 用共享的 Chat 设置或 model card 填充，各 harness 的条件会不同）。
- 每个 harness 固定版本，配置放在与用户设置分开的目录中：窗口 131,072 / 输出上限 32,768。关闭自动 compaction 与标题生成等附带请求（无法关闭的另行记录、分开计数）。tool 在工作目录内无需批准即可执行，由外部（bubblewrap）隔离。
- 每个用例与 seed 使用一次性的工作目录。测量到完成为止的实际时间、其构成（harness 启动、轮数、tool call、harness 自身前置部分的 token、prefix cache 的复用）以及成果物。
''',
}
HARNESS_LAYOUT = {
    'ja': ('コーディングのケースの成果物の置き場所',
           'ハーネスが作業ディレクトリに書いた HTML を取る（1つならそれ、複数なら index.html、なければ最後に書かれたもの）。HTML がなければ、最後の回答のコードブロックから取り出す。どちらで取ったかは manifest に残る。',
           '''<run-id>/cases/<case id>/artifact/seed-N/
  response.md     ハーネスの最後の回答
  files/          作業ディレクトリに書かれたファイル（またはコードブロックから取り出したファイル）
  manifest.json   取ったファイル、取り方（作業ディレクトリ / 回答）、形式、起動方法
  screenshot.png  単体 HTML か静的サーバーで開けた場合のみ。headless Chrome でページを 10 秒動かしてから撮る
  console.txt     そのときのエラー（捕まえられなかった例外、console.error、読み込みの失敗）。manifest の screenshot に、描画されたか（ほぼ一色・輪郭なしなら空白）と、固まったか（読み込みが CDN で止まっただけなら「読み込み待ち」）も残る''',
           'ハーネスの出力（イベント）とプロキシの記録（各リクエスト）は `harness/seed-N/` に残る。'),
    'en': ('Where the coding cases\' results go',
           'The HTML the harness wrote into its work folder is taken (the one there is, else index.html, else the last one written). With no HTML file, the files come from the code blocks of the last answer. The manifest says which.',
           '''<run-id>/cases/<case id>/artifact/seed-N/
  response.md     the harness's last answer
  files/          the files written into the work folder (or taken from the code blocks)
  manifest.json   the files, where they came from (work folder / answer), the form, how to run it
  screenshot.png  only if it opens as a single HTML file or from a static server; taken after the page has run 10 s in headless Chrome
  console.txt     its errors then (uncaught exceptions, console.error, failed loads); the manifest's screenshot also says whether anything was drawn (nearly one colour or no edges: empty) and whether the page froze (or only stalled on a CDN)''',
           'The harness\'s output (its events) and the proxy\'s record (every request) are kept in `harness/seed-N/`.'),
    'zh': ('编程用例的成果存放位置',
           '取 harness 写入工作目录的 HTML（只有一个就取它，多个则取 index.html，否则取最后写入的）。没有 HTML 文件时，从最后回答的代码块中取出。取法记录在 manifest 中。',
           '''<run-id>/cases/<case id>/artifact/seed-N/
  response.md     harness 的最后回答
  files/          写入工作目录的文件（或从代码块中取出的文件）
  manifest.json   取出的文件、来源（工作目录 / 回答）、形式、运行方法
  screenshot.png  仅当能以单个 HTML 或静态服务器打开时。在 headless Chrome 中让页面运行 10 秒后截图
  console.txt     当时的错误（未捕获的异常、console.error、加载失败）；manifest 的 screenshot 还记录是否画出了内容（几乎一种颜色或没有轮廓则为空白）以及页面是否卡死''',
           'harness 的输出（事件）和代理的记录（每个请求）保存在 `harness/seed-N/`。'),
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


def engine_label(engine_id):
    return engines.entry(engine_id)['label']


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
                    f'[{L("部門の一覧", "All divisions", "部门一览")}]({up}divisions/README{suffix if (ROOT / f"divisions/README{suffix}.md").exists() else ""}.md)\n')
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
            (L('基準モデル', 'reference model', '基准模型'), (' '.join(case_plan.REF) if case_plan.REF else '–') + ' ' + L(
                '（env.json の ref、なければ Strata がこの RAM + VRAM に勧めるモデル）', '(env.json "ref", else the model Strata recommends for this RAM + VRAM)',
                '（env.json 的 ref，否则为 Strata 针对此 RAM + VRAM 推荐的模型）')),
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
                    f'| {L("エンジン", "engine", "引擎")} | family | model | GB | {L("種別", "kind", "类别")} | '
                    f'{L("測った版（リポジトリ @ コミット、RUN_ID の models.json）", "version measured (repository @ commit, the RUN_ID's models.json)", "测量的版本（仓库 @ 提交，RUN_ID 的 models.json）")} |\n'
                    '| --- | --- | --- | ---: | --- | --- |\n')
        text[-1] += ''.join(f'| {engine_label(case_plan.ENGINES_OF[(f, m)][0])} | {f} | {display_model(f, m)} | {gb} | {md(tr(role, lang))} | {versions.get((f, m), "–")} |\n'
                            for f, m, gb, role in page_models(rows))
        harness = division.get('harness')
        text.append(f'\n## {L("全ケース共通の条件", "Conditions shared by every case", "所有用例的共同条件")}\n\n{(HARNESS_COMMON if harness else COMMON)[lang]}')
        title, intro, tree, after = (HARNESS_LAYOUT if harness else GAME_LAYOUT)[lang]
        text.append(f'\n<details><summary>{title}</summary>\n\n{intro}\n\n```\n{tree}\n```\n\n{after}\n\n</details>\n')
        text.append(f'\n<details><summary>{L("見積もりの前提（rtx5090-128g の初回の計測の中央値。ほかの環境は env.json の assume で上書き）", "What the estimate assumes (medians of the first run on rtx5090-128g; other environments override them in env.json \"assume\")", "预估的前提（rtx5090-128g 首次测量的中位数；其他环境在 env.json 的 assume 中覆盖）")}</summary>\n\n'
                    f'```json\n{json.dumps(ASSUME, ensure_ascii=False, indent=2)}\n```\n\n</details>\n')
        (out / f'README{suffix}.md').write_text('\n'.join(text))

        for step in steps:
            lst = [r for r in rows if r['step'] == step]
            labels = dict(COLUMNS)
            head = ([L('状態', 'status', '状态')] + [heading(labels.get(k, k), lang) for k in TIER_COLS]
                    + [L('結果', 'result', '结果'), L('エビデンス', 'evidence', '证据')])
            body, by_engine = [], list(dict.fromkeys(r.get('engine') or engines.DEFAULT for r in lst))
            for r in sorted(lst, key=lambda r: by_engine.index(r.get('engine') or engines.DEFAULT)):   # one table per engine
                if len(by_engine) > 1 and (r.get('engine') or engines.DEFAULT) != (body and body[-1][0]):
                    body.append((r.get('engine') or engines.DEFAULT, None))
                cells = []
                for k in TIER_COLS:
                    if k == 'id':
                        cells.append(f'`{r["id"]}`')
                    elif k == 'model':
                        cells.append(f'{r["family"]} {display_model(r["family"], r["model"])}')
                    elif k == 'context_label':
                        cells.append(r['context_label'] + (f' (YaRN {r["yarn"]})' if r.get('yarn') else ''))
                    else:
                        cells.append(md(tr(cell(r[k], k), lang)))
                body.append((r.get('engine') or engines.DEFAULT,
                             '| ' + ' | '.join([r['status']] + cells + [md(result_md(r, lang)), evidence_md(r, up)]) + ' |'))
            info = L(*TIER_INFO[step]) if step in TIER_INFO else ''
            page = [langs_line(f'tier-{step}'), f'[{L("← ケース一覧", "← cases", "← 用例一览")}](README{suffix}.md)\n',
                    f'# Tier {step}: {info}\n', f'{envs.label(cfg)} · ' + L(
                        f'{len(lst):,} ケース / {sum(r["reps"] for r in lst):,} リクエスト。ほかのパラメータ（入力の内容、見るもの、備考、seed、timeout、起動セッション）は [tier-{step}.csv](tier-{step}.csv)。',
                        f'{len(lst):,} cases / {sum(r["reps"] for r in lst):,} requests. The other parameters (input, measures, notes, seeds, timeout, launch session) are in [tier-{step}.csv](tier-{step}.csv).',
                        f'{len(lst):,} 个用例 / {sum(r["reps"] for r in lst):,} 个请求。其他参数（输入内容、测量内容、备注、seed、timeout、启动会话）见 [tier-{step}.csv](tier-{step}.csv)。') + '\n',
                    ]
            table = ['| ' + ' | '.join(head) + ' |', '| ' + ' | '.join(['---'] * len(head)) + ' |']
            if len(by_engine) < 2:
                page += table
            for eng, line in body:
                page += [f'\n## {engine_label(eng)}\n', *table] if line is None else [line]
            page.append('')
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
    rows = [r for r in rows if not r.get('retired')]   # measured before; not run again
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
    ap.add_argument('--env', default='', help='only this environment (default: every one the pages show)')
    ap.add_argument('--published', action='store_true',
                    help='only the runs in published/, written to cases/ (default: also results/, to preview/cases/)')
    a = ap.parse_args()
    out_root = ROOT if a.published else envs.PREVIEW
    summaries = []
    for env_id in envs.page_ids(a.published):
        cfg = envs.load(env_id, a.published)
        plan = build(cfg)
        rows = plan + measured_rows(cfg, plan, result_ids(env_id, a.published))
        attach_results(rows, env_id, a.published)
        est = estimate(plan)
        hours = sum(s['total_h'] for s in est.values())
        summaries.append({'id': env_id, 'label': envs.label(cfg), 'cases': len(rows), 'hours': hours,
                          'done': sum(r['status'] == 'done' for r in rows),
                          'failed': sum(r['status'] in ('failed', 'unreadable') for r in rows)})
        if a.env and env_id != a.env:
            continue
        if not a.published and env_id in envs.ids():   # the plan this PC measures (plan/ is outside Git)
            write_plan(plan, env_id)
        write_md(rows, out_root / 'cases' / envs.division() / env_id, cfg, a.published)
        missing = untranslated([r[k] for r in rows for k, _ in COLUMNS if k not in UNTRANSLATED_COLS]
                               + [x for m in MODELS for x in m[3:]])
        if missing:
            print(f'cases/{envs.division()}/{env_id}/: {len(missing)} string(s) without a translation in scripts/i18n.py TR (shown in Japanese):')
            for s in missing:
                print('  ' + s)
        print(f'{env_id}: {len(plan)} cases, {sum(r["requests"] for r in plan)} measured requests, ~{hours:.0f} h estimated'
              + (f' (and {len(rows) - len(plan)} measured cases of models no longer in the plan)' if len(rows) > len(plan) else ''))
        for step, s in est.items():
            print(f'  Tier {step}: {s["total_h"]} h (requests {s["request_s"] / 3600:.1f} h, launches {s["launch_s"] / 3600:.1f} h)')
    write_index(summaries, out_root, a.published)
    print(f'case lists: {os.path.relpath(out_root / "cases", ROOT)}/ ({"published/ only" if a.published else "results/ and published/"})')


if __name__ == '__main__':
    main()
