#!/usr/bin/env python3
"""The machine a run is measured on, for results/<division>/<env>/<run-id>/machine.json (written by scripts/bench_runner.py).

collect() returns the raw tool outputs the runner always kept (lscpu, nvidia-smi -q, strata --version, uname) and
"env", the parsed summary the pages show: GPU, CPU, RAM, board, the drive holding the models, OS, Strata.
Everything is read without root, except the RAM type, speed and modules: those need `sudo dmidecode -t memory`, so they
come from the environment's envs/<id>/env.json ("memory"), written by hand from its output.

    python3 -I scripts/machine_info.py results/<division>/<env>/<run-id>/machine.json <env>   # add "env" to a run recorded before it existed
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

MODELS_DIR = Path.home() / '.local/share/strata/Strata-data/models'


def run(args, env=None):
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=60,
                              env={**os.environ, **(env or {})}).stdout
    except (OSError, subprocess.SubprocessError):
        return ''


def read(path):
    try:
        return Path(path).read_text().strip()
    except OSError:
        return ''


def field(text, name):
    m = re.search(rf'^\s*{re.escape(name)}\s*:\s*(.+)$', text, re.M)
    return m.group(1).strip() if m else None


def drive_of(path):
    """The model name of the disk holding path (an NVMe partition -> its controller's model)."""
    src = run(['findmnt', '-no', 'SOURCE', '-T', str(path)]).strip()
    dev = Path(src).name
    m = re.match(r'(nvme\d+)n\d+', dev)
    if m:
        return read(f'/sys/class/nvme/{m.group(1)}/model') or None, 'NVMe'
    disk = re.sub(r'\d+$', '', dev)
    return read(f'/sys/block/{disk}/device/model') or None, None


def env_summary(lscpu_c, smi, memory):
    os_release = dict(re.findall(r'^(\w+)="?([^"\n]*)"?$', read('/etc/os-release'), re.M))
    mem_kb = int(re.search(r'MemTotal:\s+(\d+)', read('/proc/meminfo')).group(1))
    gpu_q = run(['nvidia-smi', '--query-gpu=name,memory.total,pcie.link.gen.max,pcie.link.width.max',
                 '--format=csv,noheader,nounits']).strip().split(', ')
    threads = int(field(lscpu_c, 'CPU(s)') or 0)
    cores = int(field(lscpu_c, 'Core(s) per socket') or 0) * int(field(lscpu_c, 'Socket(s)') or 1)
    drive, bus = drive_of(MODELS_DIR)
    limit = re.search(r'Current Power Limit\s+:\s+([\d.]+) W', smi)
    default = re.search(r'Default Power Limit\s+:\s+([\d.]+) W', smi)
    return {
        'gpu': gpu_q[0] if gpu_q and gpu_q[0] else field(smi, 'Product Name'),
        'gpu_vram_mib': int(gpu_q[1]) if len(gpu_q) > 1 and gpu_q[1].isdigit() else None,
        'gpu_pcie': f'PCIe {gpu_q[2]}.0 x{gpu_q[3]}' if len(gpu_q) > 3 else None,
        'gpu_driver': field(smi, 'Driver Version'), 'cuda': field(smi, 'CUDA Version'),
        'gpu_power_limit_w': float(limit.group(1)) if limit else None,
        'gpu_power_default_w': float(default.group(1)) if default else None,
        'cpu': field(lscpu_c, 'Model name'), 'cpu_cores': cores, 'cpu_threads': threads,
        'cpu_max_mhz': round(float(field(lscpu_c, 'CPU max MHz') or 0)) or None,
        'cpu_governor': read('/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor') or None,
        'ram_gib': round(mem_kb / 1048576, 1),
        'ram_modules': {k: memory.get(k) for k in ('type', 'speed_mts', 'configured_mts', 'modules', 'channels', 'recorded_at')}
                       if memory else None,
        'board': ' '.join(x for x in [read('/sys/class/dmi/id/board_vendor'), read('/sys/class/dmi/id/board_name')] if x) or None,
        'models_drive': drive, 'models_drive_bus': bus,
        'os': os_release.get('PRETTY_NAME'), 'kernel': os.uname().release,
    }


def collect(p_cores=None, memory=None):
    """memory: the environment's hand-written RAM details (envs/<id>/env.json), which need root to read."""
    lscpu = run(['lscpu'])
    smi = run(['nvidia-smi', '-q'])[:20000]
    strata = run(['strata', '--version']).strip()
    env = env_summary(run(['lscpu'], {'LC_ALL': 'C'}), smi, memory)
    env['strata'] = re.sub(r';\s*python .*\)', ')', strata)   # without the install path
    out = {'lscpu': lscpu, 'nvidia_smi': smi, 'strata': strata, 'uname': ' '.join(os.uname()), 'env': env}
    if p_cores is not None:
        out['p_cores'] = p_cores
    return out


def latest_env(root, env_id, published_only=False):
    """The env of the environment's newest run that has one (test- runs left out), else None."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import envs
    for d in reversed(envs.run_dirs(env_id, published_only)):
        p = d / 'machine.json'
        try:
            env = json.loads(p.read_text()).get('env')
        except (OSError, ValueError):
            env = None
        if env:
            return env, p.parent.name
    return None, None


def env_for(root, cfg, published_only=False):
    """One environment's machine: its newest run's record; before any run, this machine now if it is that environment,
    else what env.json says. Returns (env, the run id it was recorded for or None)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import envs
    env, run_id = latest_env(root, cfg['id'], published_only)
    if not env and envs.detect()[0] == cfg['id']:
        env = collect(memory=cfg.get('memory'))['env']
    if not env:
        hw = cfg.get('hardware') or {}
        env = {'gpu': (cfg.get('match') or {}).get('gpu'), 'gpu_vram_mib': (hw.get('gpu_vram_gib') or 0) * 1024 or None,
               'ram_gib': hw.get('ram_gib'), 'ram_modules': cfg.get('memory'), 'gpu_power_limit_w': cfg.get('gpu_power_limit_w')}
    return env, run_id


def env_box(root, cfg, published_only=False, how=True):
    """The environment box for one environment (env_for)."""
    return env_html(*env_for(root, cfg, published_only), cfg, how)


def env_md(root, cfg, lang, published_only=False):
    """The same as a Markdown table in one language (the case lists, read on GitHub)."""
    from i18n import one
    L = one(lang)
    env, run_id = env_for(root, cfg, published_only)
    rows, src = env_rows(env, run_id, cfg, L)
    return ('| | |\n| --- | --- |\n' + ''.join(f'| {k} | {v} |\n' for k, v in rows if v)
            + f'\n{how_html(L)}\n\n{src}\n')


def ram_text(env, installed, L=None):
    if L is None:
        from i18n import L
    if not installed:
        return '?'
    m = env.get('ram_modules') or {}
    mods = m.get('modules') or []
    sizes = {x.get('size_gib') for x in mods}
    if m.get('type') and mods and len(sizes) == 1:
        size, n, ch = sizes.pop(), len(mods), m.get('channels')
        kind = f'{m["type"]}-{m.get("configured_mts") or m.get("speed_mts")} {size} GB × {n}'
        layout = L(f'、{ch} チャネル' if ch else '', f', {ch} channels' if ch else '', f'，{ch} 通道' if ch else '')
        return L(f'{installed:.0f} GB（{kind}', f'{installed:.0f} GB ({kind}', f'{installed:.0f} GB（{kind}') + layout + L(
            f'。OS から見えるのは {env["ram_gib"]} GiB）', f'; {env["ram_gib"]} GiB visible to the OS)', f'；操作系统可见 {env["ram_gib"]} GiB）')
    return L(f'{installed:.0f} GB（OS から見えるのは {env["ram_gib"]} GiB）', f'{installed:.0f} GB ({env["ram_gib"]} GiB visible to the OS)',
             f'{installed:.0f} GB（操作系统可见 {env["ram_gib"]} GiB）')


def how_html(L=None):
    """How the measurements are taken (the desktop app is not used), in all three languages (L: i18n.one(lang) for one)."""
    if L is None:
        from i18n import L
    return L('Strata のデスクトップアプリは使っていない。CLI の <code>strata launch --no-tui</code> でエンジンを専用ポート（18600）に起動し、'
            'OpenAI 互換の HTTP API（<code>POST /v1/chat/completions</code>、ストリーミング）を <code>scripts/bench_runner.py</code> から直接呼んで測る。'
            'Tier 2 だけは Strata 同梱のベンチ <code>strata bench run --suite standard-v1</code> を同じエンジンに向けて実行する。',
            'The Strata desktop app is not used. The CLI (<code>strata launch --no-tui</code>) starts the engine on a dedicated port (18600), and '
            '<code>scripts/bench_runner.py</code> calls its OpenAI-compatible HTTP API (<code>POST /v1/chat/completions</code>, streaming) directly. '
            'Only Tier 2 runs Strata\'s bundled benchmark, <code>strata bench run --suite standard-v1</code>, against the same engine.',
            '未使用 Strata 桌面应用。用 CLI <code>strata launch --no-tui</code> 在专用端口（18600）启动引擎，由 '
            '<code>scripts/bench_runner.py</code> 直接调用其 OpenAI 兼容的 HTTP API（<code>POST /v1/chat/completions</code>，流式）进行测量。'
            '只有 Tier 2 是对同一引擎运行 Strata 自带的基准测试 <code>strata bench run --suite standard-v1</code>。', escape=False)


def env_html(env, run_id, cfg=None, how=True):
    """The "where this was measured" box at the top of RESULTS.html, in all three languages; how=False
    leaves out the paragraph on how it is measured (RESULTS.html shows it with its introduction)."""
    from i18n import L
    rows, src = env_rows(env, run_id, cfg, L)
    return ('<style>.envbox { margin: 14px 0 0; padding: 10px 14px; background: var(--surface); border: 1px solid var(--border); '
            'border-radius: 8px; font-size: 13px; } .envbox h2 { font-size: 14px; margin: 0 0 6px; padding: 0; } '
            '.envbox dl { display: grid; grid-template-columns: max-content 1fr; gap: 3px 14px; margin: 0; } '
            '.envbox dt { color: var(--muted); } .envbox dd { margin: 0; min-width: 0; overflow-wrap: anywhere; } '
            '.envbox .how { margin: 8px 0 0; } .envbox .src { color: var(--muted); font-size: 12px; margin: 6px 0 0; } '
            '@media (max-width: 640px) { .envbox dl { grid-template-columns: 1fr; } .envbox dd { margin-bottom: 4px; } }</style>'
            f'<section class="envbox" id="env"><h2>{L("実行環境", "Test system", "运行环境")}</h2><dl>'
            + ''.join(f'<dt>{k}</dt><dd>{v}</dd>' for k, v in rows if v)
            + '</dl>' + (f'<p class="how">{how_html()}</p>' if how else '') + f'<p class="src">{src}</p></section>')


def env_rows(env, run_id, cfg, L):
    """The box's (label, value) rows and its source line; L picks the language(s) (i18n.L, or i18n.one(lang))."""
    import html
    e = lambda v: html.escape(str(v)) if v not in (None, '') else '?'  # noqa: E731
    board = (env.get('board') or '').replace('Micro-Star International Co., Ltd.', 'MSI')
    cpu = re.sub(r'\((R|TM)\)', '', env.get('cpu') or '').replace('  ', ' ')
    ram_installed = -(-env['ram_gib'] // 16) * 16 if env.get('ram_gib') else None   # MemTotal is a little below the modules
    vram = f'{round(env["gpu_vram_mib"] / 1024)} GB' if env.get('gpu_vram_mib') else '?'
    lim, dflt = env.get('gpu_power_limit_w'), env.get('gpu_power_default_w')
    ghz = f'{env["cpu_max_mhz"] / 1000:.1f} GHz' if env.get('cpu_max_mhz') else '?'
    rows = [
        ('GPU', f'{e(env.get("gpu"))} ({vram}, {e(env.get("gpu_pcie"))}) · driver {e(env.get("gpu_driver"))} / CUDA {e(env.get("cuda"))} · '
                + (L(f'電力上限 {lim:.0f} W（既定 {dflt:.0f} W）', f'power limit {lim:.0f} W (default {dflt:.0f} W)',
                     f'功耗上限 {lim:.0f} W（默认 {dflt:.0f} W）') if lim and dflt else '')),
        ('CPU', f'{e(cpu)} · ' + L(f'{env.get("cpu_cores")} コア / {env.get("cpu_threads")} スレッド、最大 {ghz}',
                                  f'{env.get("cpu_cores")} cores / {env.get("cpu_threads")} threads, up to {ghz}',
                                  f'{env.get("cpu_cores")} 核 / {env.get("cpu_threads")} 线程，最高 {ghz}')
                + f' · governor {e(env.get("cpu_governor"))}'),
        (L('メモリ', 'Memory', '内存'), ram_text(env, ram_installed, L)),
        (L('マザーボード', 'Motherboard', '主板'), e(board)),
        (L('モデルの置き場所', 'Model storage', '模型存放'), f'{e(env.get("models_drive"))} ({e(env.get("models_drive_bus"))})'),
        ('OS', f'{e(env.get("os"))} (Linux {e(env.get("kernel"))})'),
        ('Strata', e(env.get('strata'))),
    ]
    src = (L(f'RUN_ID {run_id} の記録（machine.json）', f'as recorded for RUN_ID {run_id} (machine.json)', f'RUN_ID {run_id} 的记录（machine.json）')
           if run_id else L('まだ計測の記録が無いので、env.json とこの PC の現在の構成から', 'no run recorded yet: from env.json and this PC now',
                            '尚无测量记录：来自 env.json 和本机当前配置'))
    if cfg:
        src = L('環境', 'environment', '环境') + f' <code>{html.escape(cfg["id"])}</code> · ' + src
    return rows, src


def main():
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import envs
    path = Path(sys.argv[1])
    data = json.loads(path.read_text())
    new = collect(memory=envs.load(sys.argv[2]).get('memory'))
    data['env'] = {**data.get('env', {}), **new['env']}
    # The GPU power limit belongs to the time of the run, not to now.
    limit = re.search(r'Current Power Limit\s+:\s+([\d.]+) W', data.get('nvidia_smi', ''))
    data['env']['gpu_power_limit_w'] = float(limit.group(1)) if limit else None
    data['env']['strata'] = re.sub(r';\s*python .*\)', ')', data.get('strata', '')) or new['env']['strata']
    data['env_added_at'] = __import__('datetime').datetime.now().astimezone().isoformat(timespec='seconds')
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(data['env'], indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
