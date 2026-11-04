#!/usr/bin/env python3
"""Make a finished run final: move it from results/<division>/<env>/<run id>/ (ignored by Git) to published/<division>/<env>/<run id>/
(tracked), then rebuild the committed pages from published/ alone (CASES.html, cases/, RESULTS.html, published/summary.csv).

    python3 -I scripts/publish.py <env> <run id> --dry-run    # what would move, and its size (division: $BENCH_DIVISION, default plain)
    python3 -I scripts/publish.py <env> <run id> --note "what this run is"
    python3 -I scripts/publish.py --readme                    # only rebuild the READMEs' list of published runs

Each publish also rewrites the list of published runs in README.md, README.en.md and README.zh.md (between their published-runs markers), from published/
alone; --note is the run's one line there (kept as published/<division>/<env>/<run id>/NOTE.md; --note-en / --note-zh as NOTE.en.md / NOTE.zh.md, the Japanese one where they are missing).

What stays behind in results/<division>/<env>/<run id>/, never published: raw/ (the SSE streams and thinking text) and the
machine snapshots (stats/snapshots.jsonl.gz, stats/last.json: every program's command line on the PC).
stats/thermal.csv (temperatures, power, clocks) is published with the run.

Every text file published has the home folder written as ~ and the PC's host name as <host> (engine logs, launch output
and machine.json name both). python3 -I scripts/publish.py --scrub does the same to what is in published/ already.

Refused: test- runs, a run whose queue has not finished (queue.log without "queue finished"; --force to publish
anyway, for example a run that was stopped on purpose), and a run id that is already in published/.
"""
import argparse
from datetime import datetime
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import envs  # noqa: E402

ROOT = envs.ROOT
KEEP_LOCAL = {'raw'}                                     # folder names, anywhere in the run
KEEP_LOCAL_FILES = {'stats/snapshots.jsonl.gz', 'stats/last.json', 'queue.pid'}


def local_only(rel):
    parts = rel.parts
    return any(p in KEEP_LOCAL for p in parts) or rel.as_posix() in KEEP_LOCAL_FILES


HOME, HOST = str(Path.home()), os.uname().nodename


def scrub(path):
    """The home folder as ~ and the host name as <host> in a text file (binary files are left as they are)."""
    try:
        text = path.read_text(encoding='utf-8')
    except (UnicodeDecodeError, OSError):
        return False
    new = text.replace(HOME, '~')
    if HOST:
        new = re.sub(rf'(?<![\w-]){re.escape(HOST)}(?![\w-])', '<host>', new)
    if new != text:
        path.write_text(new, encoding='utf-8')
    return new != text


def scrub_published():
    files = [p for p in envs.PUBLISHED.rglob('*') if p.is_file()]
    n = sum(scrub(p) for p in files)
    print(f'published/: {n} of {len(files)} files had the home folder or the host name')


def size(paths):
    return sum(p.stat().st_size for p in paths if p.is_file())


# README.md (Japanese), README.en.md and README.zh.md each carry the list; a run's line in each is NOTE.md, NOTE.en.md,
# NOTE.zh.md (the Japanese one where a translation is missing)
READMES = {'ja': ROOT / 'README.md', 'en': ROOT / 'README.en.md', 'zh': ROOT / 'README.zh.md'}
HEAD = {'ja': ['計測完了', '部門', '環境', 'RUN_ID', 'Tier', 'ケース（done / 全体）', '内容', '見る'],
        'en': ['Finished', 'Division', 'Environment', 'RUN_ID', 'Tier', 'Cases (done / all)', 'Content', 'See'],
        'zh': ['测量完成', '部门', '环境', 'RUN_ID', 'Tier', '用例（done / 全部）', '内容', '查看']}
LINKS = {'ja': ('グラフ', 'ケース一覧'), 'en': ('Charts', 'Cases'), 'zh': ('图表', '用例一览')}
NONE = {'ja': 'まだ確定した結果はありません', 'en': 'No published runs yet', 'zh': '尚无已确定的结果'}
MARK = ('<!-- published-runs:start (scripts/publish.py writes this list) -->', '<!-- published-runs:end -->')
TIER_ORDER = ['0', '1', '2', '3', '4a', '4b', '4c', '4d', '5']


def run_rows():
    """One row per published run, the last to finish first: when it finished, its division and environment, its Tiers and cases,
    its note."""
    rows = []
    for d in sorted(envs.PUBLISHED.glob('*/*/*/cases')):
        run, env_id, div = d.parent, d.parent.parent.name, d.parents[2].name
        label = envs.load(env_id).get('label', env_id)
        steps = {c.name.split('-', 1)[0][1:] for c in d.iterdir() if c.is_dir()}
        done = sum(json.loads(s.read_text()).get('status') == 'done' for s in d.glob('*/summary.json'))
        total = len(list(d.glob('*/summary.json')))
        q = (run / 'queue.log').read_text(errors='replace') if (run / 'queue.log').exists() else ''
        ends = re.findall(r'^(\d{4}-\d\d-\d\dT\S+) queue finished', q, re.M)   # the last finish, to the second
        notes = {lang: (run / name).read_text().strip() for lang, name in (('ja', 'NOTE.md'), ('en', 'NOTE.en.md'), ('zh', 'NOTE.zh.md'))
                 if (run / name).exists()}
        rows.append({'div': div, 'div_label': envs.load_division(div)['label'], 'env': env_id, 'label': label, 'run': run.name, 'finished': ends[-1] if ends else '', 'date': ends[-1][:16].replace('T', ' ') if ends else '?', 'notes': notes,
                     'tiers': ', '.join(t for t in TIER_ORDER if t in steps), 'cases': f'{done} / {total}'})
    return sorted(rows, key=lambda r: (datetime.fromisoformat(r['finished']).timestamp() if r['finished'] else 0, r['run']), reverse=True)


def update_readme():
    """Rewrite the list of published runs (between MARK) in each README, from published/."""
    rows = run_rows()
    for lang, path in READMES.items():
        if not path.exists():
            continue
        text = path.read_text()
        if MARK[0] not in text or MARK[1] not in text:
            raise SystemExit(f'{path.name} has no {MARK[0]} … {MARK[1]} block')
        lines = ['| ' + ' | '.join(HEAD[lang]) + ' |', '| ' + ' | '.join(['---'] * len(HEAD[lang])) + ' |']
        for r in rows:
            note = r['notes'].get(lang) or r['notes'].get('ja') or '–'
            charts, cases = LINKS[lang]
            lines.append(f'| {r["date"]} | {r["div_label"][lang]} | {r["label"]} | [`{r["run"]}`](published/{r["div"]}/{r["env"]}/{r["run"]}/) | '
                         f'{r["tiers"]} | {r["cases"]} | {note} | '
                         f'[{charts}](RESULTS.html?env={r["env"]}) · [{cases}](cases/{r["div"]}/{r["env"]}.html) |')
        if not rows:
            lines.append('| ' + ' | '.join(['–'] * 6 + [NONE[lang], '–']) + ' |')
        head, rest = text.split(MARK[0], 1)
        path.write_text(head + MARK[0] + '\n' + '\n'.join(lines) + '\n' + MARK[1] + rest.split(MARK[1], 1)[1])
        print(f'{path.name}: {len(rows)} published run(s) listed')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('env', nargs='?')
    ap.add_argument('run_id', nargs='?')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--force', action='store_true', help='publish a run whose queue did not finish')
    ap.add_argument('--note', default='', help="the run's one line in README.md's list (published/<division>/<env>/<run id>/NOTE.md)")
    ap.add_argument('--note-en', default='', help='the same line in English (NOTE.en.md, README.en.md)')
    ap.add_argument('--note-zh', default='', help='the same line in Chinese (NOTE.zh.md, README.zh.md)')
    ap.add_argument('--readme', action='store_true', help="only rebuild the READMEs' list of published runs")
    ap.add_argument('--scrub', action='store_true', help='write ~ and <host> into what is in published/ already')
    a = ap.parse_args()
    if a.readme:
        return update_readme()
    if a.scrub:
        return scrub_published()
    if not (a.env and a.run_id):
        ap.error('env and run_id are needed (or --readme)')
    envs.load(a.env)
    src = envs.run_dir(a.env, a.run_id)
    dst = envs.published_dir(a.env, a.run_id)
    if a.run_id.startswith('test-'):
        raise SystemExit('test- runs are not published')
    if not (src / 'cases').is_dir():
        raise SystemExit(f'{src.relative_to(ROOT)} has no cases/')
    if dst.exists():
        raise SystemExit(f'{dst.relative_to(ROOT)} already exists; publish under a new run id, or remove it first')
    queue = src / 'queue.log'
    finished = queue.exists() and 'queue finished' in queue.read_text(errors='replace')
    if not finished and not a.force:
        raise SystemExit(f'the queue of {a.run_id} has not finished ({queue.relative_to(ROOT)}); --force to publish it anyway')

    files = [p for p in src.rglob('*') if p.is_file()]
    move = [p for p in files if not local_only(p.relative_to(src))]
    stay = [p for p in files if local_only(p.relative_to(src))]
    cases = len(list(src.glob('cases/*/summary.json')))
    print(f'{src.relative_to(ROOT)} -> {dst.relative_to(ROOT)}: {cases} cases, {len(move)} files, {size(move) / 1e6:.1f} MB')
    print(f'stays in {src.relative_to(ROOT)} (not published): {len(stay)} files, {size(stay) / 1e6:.1f} MB (raw/, machine snapshots)')
    if a.dry_run:
        return
    for p in move:
        target = dst / p.relative_to(src)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(p), str(target))
        scrub(target)
    for d in sorted((d for d in src.rglob('*') if d.is_dir()), key=lambda d: len(d.parts), reverse=True):
        if not any(d.iterdir()):
            d.rmdir()
    for text, name in ((a.note, 'NOTE.md'), (a.note_en, 'NOTE.en.md'), (a.note_zh, 'NOTE.zh.md')):
        if text:
            (dst / name).write_text(text.strip() + '\n')
    for script in ('build_cases.py', 'build_results.py'):
        subprocess.run([sys.executable, '-I', str(ROOT / 'scripts' / script), '--published'], check=True, cwd=ROOT)
    update_readme()
    subprocess.run([sys.executable, '-I', str(ROOT / 'scripts' / 'tuned_configs.py')], check=True, cwd=ROOT)
    print(f'published. Commit {os.path.relpath(dst, ROOT)}/ with CASES.html, cases/, RESULTS.html, published/summary.csv, README*.md and configs/tuned/')


if __name__ == '__main__':
    main()
