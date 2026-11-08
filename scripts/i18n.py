"""Japanese / English / Chinese for the charts (RESULTS) and the case lists (cases/).

The plan (build_cases.py) and the results keep their Japanese text as the data; the pages show it in the reader's
language. TR translates those data strings, L() writes one piece of page text in all three languages (one(lang): the
same for one language, as the case lists have a Markdown file per language), and HEAD / SWITCH / SCRIPT are the
charts' language switcher (the choice: ?lang=, then the last one picked,
then the browser's language). Without JavaScript the page shows Japanese.

A data string missing from TR is shown in Japanese; untranslated() lists them, and both build scripts print them.
"""
import html

LANGS = [('ja', '日本語'), ('en', 'English'), ('zh', '中文')]

# Japanese data string -> (English, Chinese)
TR = {
    # model roles (build_cases.MODELS)
    '元重みの量子化 (ISTA)': ('quantized from the original weights (ISTA)', '原始权重量化（ISTA）'),
    '元重みの量子化 (ISTA)、基準モデル': ('quantized from the original weights (ISTA), the reference model',
                                    '原始权重量化（ISTA），基准模型'),
    '元重みの量子化 (trellis)': ('quantized from the original weights (trellis)', '原始权重量化（trellis）'),
    '元重みの量子化 (Unsloth)': ('quantized from the original weights (Unsloth)', '原始权重量化（Unsloth）'),
    '元重みの量子化 (Unsloth)、品質の参照点': ('quantized from the original weights (Unsloth), the quality reference',
                                       '原始权重量化（Unsloth），质量参照点'),
    '元重みの量子化 (Unsloth v3.1)': ('quantized from the original weights (Unsloth v3.1)', '原始权重量化（Unsloth v3.1）'),
    '元重みの量子化 (GPTQ)': ('quantized from the original weights (GPTQ)', '原始权重量化（GPTQ）'),
    '元重みの量子化 (RTN)': ('quantized from the original weights (RTN)', '原始权重量化（RTN）'),
    'expert 半減の剪定版': ('pruned to half the experts', 'expert 减半的剪枝版'),
    'fine-tune（思考が短い）': ('fine-tune (shorter thinking)', 'fine-tune（思考较短）'),
    'FP4 向け再学習版': ('retrained for FP4', '针对 FP4 重新训练的版本'),
    # input contents
    '日本語の説明文': ('Japanese explanatory prose', '日语说明文'),
    '英語の説明文': ('English explanatory prose', '英语说明文'),
    '構造化出力 (JSON)': ('structured output (JSON)', '结构化输出（JSON）'),
    'Python 実装': ('a Python implementation', 'Python 实现'),
    '渡した文章の書き写し': ('copying a given text', '照抄给定的文章'),
    'standard-v1 と同じ作り方の固定レコード列': ('fixed records built the same way as standard-v1',
                                        '与 standard-v1 相同方式生成的固定记录'),
    'standard-v1 固定 fixture': ('standard-v1 fixed fixture', 'standard-v1 固定 fixture'),
    '数学': ('math', '数学'),
    'コード（テスト実行で判定）': ('code (judged by running tests)', '代码（运行测试判定）'),
    '日本語の推論': ('reasoning in Japanese', '日语推理'),
    '英語の推論': ('reasoning in English', '英语推理'),
    '10% の位置の事実': ('a fact at 10% of the document', '位于文档 10% 处的事实'),
    '50% の位置の事実': ('a fact at 50% of the document', '位于文档 50% 处的事实'),
    '90% の位置の事実': ('a fact at 90% of the document', '位于文档 90% 处的事实'),
    '離れた複数箇所の統合': ('combining several distant passages', '整合多处相隔较远的内容'),
    '4K の文章 + 続きを書く指示': ('a 4K text + an instruction to continue it', '4K 文章 + 续写指令'),
    '「マイクラ風3D箱庭ゲーム作って」（実用的なコーディング）': (
        '“マイクラ風3D箱庭ゲーム作って” (make a Minecraft-like 3D sandbox game; practical coding, sent in Japanese)',
        '“マイクラ風3D箱庭ゲーム作って”（做一个类似 Minecraft 的 3D 沙盒游戏；实用编程，以日语原文发送）'),
    # input tokens, seeds, YaRN
    '短文': ('short', '短文'),
    '固定': ('fixed', '固定'),
    '1,2,3 × 起動 3 回': ('1,2,3 × 3 launches', '1,2,3 × 启动 3 次'),
    '1（スイートを 3 回実行）': ('1 (the suite runs 3 times)', '1（整个套件运行 3 次）'),
    'なし': ('none', '无'),
    # configs (Tier 5) and their launch options
    'baseline=既定': ('baseline=default', 'baseline=默认'),
    'cpu-pin=P コアのみ': ('cpu-pin=P-cores only', 'cpu-pin=仅 P 核'),
    '--pool-cores <P コアの論理 CPU>': ('--pool-cores <the P-cores\' logical CPUs>', '--pool-cores <P 核的逻辑 CPU>'),
    # what each case measures
    'decode tok/s, MTP 採用率': ('decode tok/s, MTP acceptance rate', 'decode tok/s、MTP 接受率'),
    'prefill tok/s, TTFT, 長文後の decode': ('prefill tok/s, TTFT, decode after the long input',
                                         'prefill tok/s、TTFT、长输入后的 decode'),
    'prefill tok/s, TTFT, 長文後の decode, RAM / VRAM peak, 正答': (
        'prefill tok/s, TTFT, decode after the long input, RAM / VRAM peak, correct answers',
        'prefill tok/s、TTFT、长输入后的 decode、RAM / VRAM 峰值、正确答案'),
    'decode tok/s を GYRO.md の 5090 の値と比較': ('decode tok/s against the 5090 figures in GYRO.md',
                                               'decode tok/s 与 GYRO.md 中 5090 的数值对比'),
    'prefill tok/s を GYRO.md の 5090 の値と比較': ('prefill tok/s against the 5090 figures in GYRO.md',
                                                'prefill tok/s 与 GYRO.md 中 5090 的数值对比'),
    'decode tok/s, expert cache スロット数, VRAM / RAM peak, 起動可否': (
        'decode tok/s, expert cache slots, VRAM / RAM peak, whether it launches',
        'decode tok/s、expert cache 槽位数、VRAM / RAM 峰值、能否启动'),
    'prefill / decode / 回答までの時間': ('prefill / decode / time to the answer', 'prefill / decode / 到回答的时间'),
    '正答': ('correct answers', '正确答案'),
    '正答, prefill / decode tok/s': ('correct answers, prefill / decode tok/s', '正确答案、prefill / decode tok/s'),
    '正答（文書部分は prefix cache を使う）': ('correct answers (the document comes from the prefix cache)',
                                     '正确答案（文档部分使用 prefix cache）'),
    '思考 token 数, 回答までの時間, 完了時間, 正答, cap 到達': (
        'thinking tokens, time to the answer, total time, correct answers, cap reached',
        '思考 token 数、到回答的时间、完成时间、正确答案、是否触及 cap'),
    '完了時間, 出力 token, cap 到達, 成果物が動くか': (
        'total time, output tokens, cap reached, whether the result runs',
        '完成时间、输出 token、是否触及 cap、成果能否运行'),
    'decode tok/s, DFlash2 採用率': ('decode tok/s, DFlash2 acceptance rate', 'decode tok/s、DFlash2 接受率'),
    # notes
    'drafter なし': ('no drafter', '不使用 drafter'),
    '0.2.10 から Auto はこのモデルで DFlash2 を選ぶ（ほかのケースは MTP に固定）。drafter（1.2 GB）は計測前に取得しておく': (
        'since 0.2.10 Auto picks DFlash2 for this model (every other case pins MTP). The drafter (1.2 GB) is fetched before measuring',
        '自 0.2.10 起 Auto 会为此模型选择 DFlash2（其他用例固定为 MTP）。drafter（1.2 GB）在测量前下载'),
    '同じセッション内の比較基準': ('the baseline within the same session', '同一会话内的比较基准'),
    '品質が変わる側。Tier 6 では採用しない': ('changes quality; not adopted in Tier 6', '会改变质量；Tier 6 不采用'),
    'デスクトップアプリの保存値': ('the value saved by the desktop app', '桌面应用保存的值'),
    '画像は入れない。エンコーダが VRAM を取る分の損失だけを見る': (
        'no images; only the cost of the encoder taking VRAM', '不输入图像；只看编码器占用 VRAM 带来的损失'),
    'P コア 1 つにつき 1 論理 CPU（P コアはカーネルの cpu_core の一覧、それが無ければ lscpu で2スレッドを持つコア）、CPU 0 はホストスレッド用に除く。実際の値は計測する PC で決まり、起動の記録（launch.txt）に残る': (
        'one logical CPU per P-core (the P-cores are the kernel\'s cpu_core list, or without one the cores with 2 threads in lscpu), leaving CPU 0 for the host thread. '
        "The list comes from the measuring PC and is kept in the launch record (launch.txt)",
        '每个 P 核取 1 个逻辑 CPU（P 核取自内核的 cpu_core 列表，没有该列表时取 lscpu 中有 2 个线程的核），CPU 0 留给主机线程。实际的值由测量用 PC 决定，并记录在启动记录（launch.txt）中'),
    'カードの VRAM（env.json の gpu_vram_gib）に対する割合。MiB に直した値を渡す（切り捨て）。足りずに起動できない割合もそのまま結果になる': (
        "a share of the card's VRAM (gpu_vram_gib in env.json), passed in MiB (rounded down). A share that leaves too little to start is a result as it is",
        '占显卡 VRAM（env.json 的 gpu_vram_gib）的比例，换算为 MiB 后传入（向下取整）。因空间不足而无法启动的比例也照样作为结果'),
    'クライアント並列数も 2': ('2 concurrent clients as well', '客户端并发数也为 2'),
    'クライアント並列数も 4': ('4 concurrent clients as well', '客户端并发数也为 4'),
    'tuner の所要時間も記録': ('the tuner\'s time is recorded too', '同时记录 tuner 的耗时'),
    'sampling は作者の値: top-k 20 / top-p 0.95 / min-p 0.05': (
        'sampling as the author used: top-k 20 / top-p 0.95 / min-p 0.05', 'sampling 采用作者的值：top-k 20 / top-p 0.95 / min-p 0.05'),
    '起動間のばらつきを測る。反復回数の決定に使う': (
        'measures the spread between launches; used to decide the repeat count', '测量不同启动之间的波动；用于决定重复次数'),
    'derivative（公式比較外）': ('derivative (outside the official comparison)', 'derivative（不参与官方比较）'),
    'YaRN なし': ('no YaRN', '不使用 YaRN'),
    'YaRN なし（学習長超え）。rope の flag 名は engine の解決済み設定で確認する': (
        'no YaRN (beyond the trained length). The rope flag name is checked in the engine\'s resolved settings',
        '不使用 YaRN（超出训练长度）。rope 的 flag 名称以引擎解析后的设置为准'),
    'thinking on: reasoning_effort "xhigh" + chat_template_kwargs.enable_thinking true、reasoning_budget_tokens 12,288（明示）': (
        'thinking on: reasoning_effort "xhigh" + chat_template_kwargs.enable_thinking true, '
        'reasoning_budget_tokens 12,288 (explicit)',
        'thinking on：reasoning_effort "xhigh" + chat_template_kwargs.enable_thinking true，'
        'reasoning_budget_tokens 12,288（显式指定）'),
    'thinking on: reasoning_effort "xhigh" + chat_template_kwargs.enable_thinking true、reasoning_budget_tokens 16,384'
    '（明示。ゲームは cap の半分: 3/4 だと回答のコードが途中で切れたため）。成果物は artifact/ に展開'
    '（response.md、files/、manifest.json、静的 HTML なら screenshot.png）。形式（単体 HTML / 要サーバー / README の有無）は manifest に記録': (
        'thinking on: reasoning_effort "xhigh" + chat_template_kwargs.enable_thinking true, reasoning_budget_tokens 16,384 '
        '(explicit; half the cap for the game, since at 3/4 the answer\'s code was cut off). The result is unpacked into '
        'artifact/ (response.md, files/, manifest.json, and screenshot.png for static HTML). Its form (single HTML / needs a '
        'server / has a README) is recorded in the manifest',
        'thinking on：reasoning_effort "xhigh" + chat_template_kwargs.enable_thinking true，reasoning_budget_tokens 16,384'
        '（显式指定；游戏取 cap 的一半，因为 3/4 时回答中的代码会被截断）。成果展开到 artifact/（response.md、files/、'
        'manifest.json，静态 HTML 另有 screenshot.png）。形式（单个 HTML / 需要服务器 / 有无 README）记录在 manifest 中'),
    '成果物の展開・スクリーンショットの仕組みを確かめる。thinking off: reasoning_effort "none" + '
    'chat_template_kwargs.enable_thinking false。成果物は artifact/ に展開（response.md、files/、manifest.json、'
    '静的 HTML なら screenshot.png）。形式（単体 HTML / 要サーバー / README の有無）は manifest に記録': (
        'checks the unpacking and screenshot of the result. thinking off: reasoning_effort "none" + '
        'chat_template_kwargs.enable_thinking false. The result is unpacked into artifact/ (response.md, files/, '
        'manifest.json, and screenshot.png for static HTML). Its form (single HTML / needs a server / has a README) is '
        'recorded in the manifest',
        '检查成果的展开和截图机制。thinking off：reasoning_effort "none" + chat_template_kwargs.enable_thinking false。'
        '成果展开到 artifact/（response.md、files/、manifest.json，静态 HTML 另有 screenshot.png）。'
        '形式（单个 HTML / 需要服务器 / 有无 README）记录在 manifest 中'),
}


def tr(ja, lang):
    if lang == 'ja' or ja not in TR:
        return ja
    return TR[ja][0 if lang == 'en' else 1]


def L(ja, en, zh, escape=True):
    """One piece of page text in all three languages; CSS shows the reader's."""
    e = html.escape if escape else (lambda s: s)
    return f'<span class="L ja">{e(ja)}</span><span class="L en">{e(en)}</span><span class="L zh">{e(zh)}</span>'


def one(lang):
    """L for one language (the Markdown case lists: a file per language), with the same arguments."""
    i = {'ja': 0, 'en': 1, 'zh': 2}[lang]
    return lambda ja, en, zh, escape=True: (ja, en, zh)[i]


def division_html(div, up=''):
    """The line under a page's title saying which division (divisions/<id>/division.json) its results belong to, with a
    link to the list of divisions. up: the way from the page to the repository root."""
    lab, summ = div['label'], div['summary']
    head = L('部門', 'Division', '部门')
    more = L('部門の一覧（エージェント部門は予定）', 'All divisions (the agentic ones are planned)', '部门一览（智能体部门在计划中）')
    return (f'<p class="sub division"><b>{head}: {L(lab["ja"], lab["en"], lab["zh"])}</b> — '
            f'{L(summ["ja"], summ["en"], summ["zh"])} <a href="{html.escape(up)}divisions/README.md">{more}</a></p>')


def T(ja):
    """A data string in all three languages (as it is, if it has no translation or no Japanese)."""
    if ja not in TR:
        return html.escape(ja)
    return L(ja, *TR[ja])


def untranslated(strings):
    import re
    jp = re.compile(r'[぀-ヿ一-鿿]')
    return sorted({s for s in strings if isinstance(s, str) and jp.search(s) and s not in TR})


# Shared by both pages: in <head>, the switchers' markup (light / dark beside the language), and the script that applies the choices.
HEAD = '''<style>
.L { display: none; }
:root[data-lang="ja"] .L.ja, :root[data-lang="en"] .L.en, :root[data-lang="zh"] .L.zh { display: revert; }
:root:lang(zh) body { font-family: system-ui, -apple-system, "Segoe UI", "PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif; }
.pagesw { float: right; margin: 0 0 8px 12px; display: flex; flex-wrap: wrap; gap: 8px; justify-content: flex-end; }
.langsw { display: inline-flex; border: 1px solid var(--border); border-radius: 7px; overflow: hidden; background: var(--surface); }
.langsw button { font: inherit; font-size: 14.5px; min-height: 38px; padding: 7px 14px; border: 0; background: transparent; color: var(--text); cursor: pointer; }
.langsw button + button { border-left: 1px solid var(--border); }
.langsw button.icon { font-size: 17px; min-width: 42px; padding: 5px 10px; line-height: 1; }
.langsw button[aria-pressed="true"] { background: var(--accent); color: var(--bg); font-weight: 600; }
.langsw button:focus-visible { outline: 2px solid var(--accent); outline-offset: -2px; }
</style>'''

THEMES = [('light', '☀', ('ライト', 'Light', '浅色')), ('dark', '☾', ('ダーク', 'Dark', '深色'))]   # icon only; the name is its label
SWITCH = ('<div class="pagesw">'
          '<div class="langsw" id="theme" role="group" aria-label="Light / dark · ライト / ダーク · 浅色 / 深色">'
          + ''.join(f'<button type="button" class="icon" data-theme-btn="{k}" aria-pressed="false" title="{ja}" aria-label="{ja}" '
                    f'data-attr="title,aria-label" data-ja="{ja}" data-en="{en}" data-zh="{zh}">{icon}</button>'
                    for k, icon, (ja, en, zh) in THEMES) + '</div>'
          '<div class="langsw" id="lang" role="group" aria-label="Language / 言語 / 语言">'
          + ''.join(f'<button type="button" data-lang-btn="{k}" lang="{"zh-Hans" if k == "zh" else k}" aria-pressed="{str(k == "ja").lower()}">'
                    f'{n}</button>' for k, n in LANGS) + '</div></div>')

# Elements with data-ja / data-en / data-zh get that text (or, with data-attr, those comma-separated attributes); used where a span
# cannot go (<option>, placeholder, <title>). Pages listen for "langchange" to redraw what they build in script.
SCRIPT = '''<script>
(() => {
  const root = document.documentElement, KEY = 'strata-lang', OK = ['ja', 'en', 'zh'];
  const fromUrl = new URLSearchParams(location.search).get('lang');
  let saved = null; try { saved = localStorage.getItem(KEY); } catch (e) {}
  const browser = (navigator.languages || [navigator.language || '']).map(l => l.toLowerCase().slice(0, 2)).find(l => OK.includes(l));
  const set = lang => { root.dataset.lang = lang; root.lang = lang === 'zh' ? 'zh-Hans' : lang; };
  const apply = (lang, fire) => {
    set(lang);
    document.querySelectorAll('[data-ja]').forEach(n => {
      const text = n.dataset[lang] ?? n.dataset.ja;
      if (n.dataset.attr) n.dataset.attr.split(',').forEach(a => n.setAttribute(a, text)); else n.textContent = text;
    });
    document.querySelectorAll('[data-lang-btn]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.langBtn === lang)));
    if (fire) window.dispatchEvent(new CustomEvent('langchange', { detail: lang }));
  };
  window.LANG = () => root.dataset.lang || 'ja';
  window.L = (ja, en, zh) => ({ ja, en, zh })[window.LANG()] ?? ja;
  const start = OK.includes(fromUrl) ? fromUrl : OK.includes(saved) ? saved : browser || 'en';
  set(start);   // now, so that scripts drawing the page see it
  document.addEventListener('DOMContentLoaded', () => {
    apply(start, false);
    document.getElementById('lang')?.addEventListener('click', e => {
      const lang = e.target.closest('[data-lang-btn]')?.dataset.langBtn;
      if (!lang || lang === window.LANG()) return;
      try { localStorage.setItem(KEY, lang); } catch (err) {}
      if (fromUrl) { const u = new URL(location.href); u.searchParams.set('lang', lang); history.replaceState(null, '', u); }
      apply(lang, true);
    });
  });
})();
// light / dark: a choice made here (kept per viewer) is the page's data-theme; with none the page follows the OS
(() => {
  const root = document.documentElement, KEY = 'strata-theme', OK = ['light', 'dark'];
  let saved = null; try { saved = localStorage.getItem(KEY); } catch (e) {}
  if (OK.includes(saved)) root.dataset.theme = saved;   // now, before the page paints
  const os = matchMedia('(prefers-color-scheme: dark)');
  const now = () => root.dataset.theme || (os.matches ? 'dark' : 'light');
  const show = () => document.querySelectorAll('[data-theme-btn]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.themeBtn === now())));
  os.addEventListener('change', show);
  document.addEventListener('DOMContentLoaded', () => {
    show();
    document.getElementById('theme')?.addEventListener('click', e => {
      const t = e.target.closest('[data-theme-btn]')?.dataset.themeBtn;
      if (!t || t === now()) return;
      root.dataset.theme = t;
      try { localStorage.setItem(KEY, t); } catch (err) {}
      show();
    });
  });
})();
</script>'''
