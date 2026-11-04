#!/usr/bin/env python3
"""Snapshots of the whole machine at the benchmark's key points, beside the runner (not inside it).

Follows results/<division>/<env>/<run-id>/runner.log and queue.log and takes one snapshot for each new event:
session start, engine launched, every case finished, each standard-v1 run, failures, Tier changes; and one every
--every seconds in between. A snapshot holds the processes (CPU % over one second and since the last snapshot,
RSS, disk IO), CPU use, clocks and governor, memory, pressure (PSI), disk IO, temperatures and the GPU (with its
throttle reasons and the processes holding it), and the thermal and power state: CPU throttling (events and time,
from /sys/devices/system/cpu/cpu*/thermal_throttle), the CPU power limits (PL1/PL2) and the GPU's clock-event
counters (power cap, thermal slowdown). Session starts, launches, failures and the first and last snapshot
keep every process; the others keep the busy and the large ones.

Written to results/<division>/<env>/<run-id>/stats/snapshots.jsonl.gz, one gzip member per snapshot (zcat reads them all), and
results/<division>/<env>/<run-id>/stats/thermal.csv: one row every --thermal-every seconds (temperatures, power, clocks, the share of
the time the CPU and the GPU were held back, and the runner's last event, so a slow case can be matched to the heat).
The CPU's own power (RAPL energy_uj) is readable by root only, so it is not recorded.
It holds the command lines of every program on the PC, so it stays out of Git (.gitignore).
Reading /proc for ~1 s per snapshot is light; nothing heavy runs beside a measurement.

Normally started by scripts/start_pipeline.sh as the systemd user unit strata-jbench-stats; it exits once the
queue unit (strata-jbench-queue) is no longer active.

    python3 -I scripts/stats_watch.py --run-id 2026-11-03-main
    python3 -I scripts/stats_watch.py --run-id test-x --once       one snapshot, then exit
"""
import argparse
import gzip
import json
import os
import sys
import pwd
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODELS = Path.home() / '.local/share/strata/Strata-data/models'
HZ = os.sysconf('SC_CLK_TCK')
PAGE = os.sysconf('SC_PAGE_SIZE')
SECRET = re.compile(r'((?:--)?(?:api[-_]?key|token|password|secret)[= ])\S+', re.I)

# runner.log message -> event; a "full" event keeps every process
EVENTS = [
    (re.compile(r'^start steps='), 'runner-start', True),
    (re.compile(r'^finished$'), 'runner-end', True),
    (re.compile(r'^session \S+: \d+ cases'), 'session-start', True),
    (re.compile(r'^session \S+: launched in'), 'launched', True),
    (re.compile(r'launch failed|warm-up failed|not answering|GPU already holds'), 'problem', True),
    (re.compile(r'^standard-v1 .* run \d+: rc='), 'standard-run-end', True),
    (re.compile(r'^  \S+: \w+ prefill='), 'case-end', False),
]
QUEUE_LINE = re.compile(r'^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d[+-]\d\d:\d\d (.*)$')   # the queue's own lines (date -Is)


def now():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds')


def read(path, default=''):
    try:
        return Path(path).read_text(errors='replace')
    except OSError:
        return default


# ------------------------------------------------------------------ samples

def proc_times():
    """pid -> (utime+stime ticks, rss pages, read bytes, write bytes) for every process we can read."""
    out = {}
    for d in os.scandir('/proc'):
        if not d.name.isdigit():
            continue
        st = read(f'/proc/{d.name}/stat')
        if not st:
            continue
        f = st[st.rfind(')') + 2:].split()
        io = read(f'/proc/{d.name}/io')
        r = re.search(r'read_bytes: (\d+)', io)
        w = re.search(r'write_bytes: (\d+)', io)
        out[int(d.name)] = (int(f[11]) + int(f[12]), int(f[21]), int(r.group(1)) if r else None,
                            int(w.group(1)) if w else None)
    return out


def cpu_total():
    f = read('/proc/stat').splitlines()[0].split()[1:]
    v = [int(x) for x in f]
    return {'user': v[0] + v[1], 'system': v[2] + v[5] + v[6], 'idle': v[3], 'iowait': v[4], 'steal': v[7],
            'all': sum(v[:8])}


def diskstats():
    out = {}
    for line in read('/proc/diskstats').splitlines():
        f = line.split()
        if len(f) > 13 and re.fullmatch(r'nvme\d+n\d+|sd[a-z]+', f[2]):
            out[f[2]] = (int(f[5]) * 512, int(f[9]) * 512, int(f[12]))   # read bytes, written bytes, ms busy
    return out


def proc_info(pid):
    st = read(f'/proc/{pid}/stat')
    status = read(f'/proc/{pid}/status')
    if not st:
        return None
    f = st[st.rfind(')') + 2:].split()
    uid = re.search(r'Uid:\s+(\d+)', status)
    try:
        user = pwd.getpwuid(int(uid.group(1))).pw_name if uid else None
    except KeyError:
        user = uid.group(1)
    cmd = read(f'/proc/{pid}/cmdline').replace('\0', ' ').strip() or f'[{st[st.find("(") + 1:st.rfind(")")]}]'
    return {'pid': pid, 'ppid': int(f[1]), 'state': f[0], 'user': user, 'nice': int(f[16]), 'threads': int(f[17]),
            'comm': st[st.find('(') + 1:st.rfind(')')], 'cmd': SECRET.sub(r'\1***', cmd)[:300]}


GPU_Q = ('memory.used,memory.total,utilization.gpu,utilization.memory,power.draw,power.draw.average,power.draw.instant,'
         'power.limit,enforced.power.limit,temperature.gpu,temperature.gpu.tlimit,clocks.sm,clocks.max.sm,clocks.mem,'
         'pstate,fan.speed,clocks_throttle_reasons.active')
# nvidia-smi -q -d PERFORMANCE "Clocks Event Reasons Counters" (microseconds since the driver loaded)
GPU_COUNTERS = {'SW Power Capping': 'power_cap', 'SW Thermal Slowdown': 'sw_thermal', 'HW Thermal Slowdown': 'hw_thermal',
                'HW Power Braking': 'hw_power_brake'}


def gpu_counters():
    try:
        out = subprocess.run(['nvidia-smi', '-q', '-d', 'PERFORMANCE'], capture_output=True, text=True, timeout=20).stdout
    except (OSError, subprocess.TimeoutExpired):
        return {}
    part = out.split('Clocks Event Reasons Counters', 1)[-1]
    return {key: int(m.group(1)) for name, key in GPU_COUNTERS.items()
            if (m := re.search(rf'{name}\s+:\s+(\d+) us', part))}


def cpu_throttle():
    """Totals since boot: package events and time (cpu0 holds the package's), and core events and time summed over cpus."""
    base = Path('/sys/devices/system/cpu')
    tot = {'package_events': 0, 'package_ms': 0, 'core_events': 0, 'core_ms': 0, 'cpus': 0}

    def num(p):
        try:
            return int(read(p).strip())
        except ValueError:
            return 0
    for d in base.glob('cpu[0-9]*/thermal_throttle'):
        tot['core_events'] += num(d / 'core_throttle_count')
        tot['core_ms'] += num(d / 'core_throttle_total_time_ms')
        tot['cpus'] += 1
    tot['package_events'] = num(base / 'cpu0/thermal_throttle/package_throttle_count')
    tot['package_ms'] = num(base / 'cpu0/thermal_throttle/package_throttle_total_time_ms')
    return tot


def cpu_power_limits():
    out = {}
    for c in Path('/sys/class/powercap/intel-rapl:0').glob('constraint_*_name'):
        name = read(c).strip()
        try:
            out[f'{name}_w'] = int(read(c.with_name(c.name.replace('_name', '_power_limit_uw'))).strip()) / 1e6
        except ValueError:
            pass
    return out


def throttle_delta(now_t, prev_t, cur, prev, gcur, gprev):
    """Share of the time held back between two readings: CPU package, CPU cores (averaged over cpus), GPU per reason."""
    if not prev or not prev_t:
        return {}
    ms = (now_t - prev_t) * 1000
    d = {'package_events': cur['package_events'] - prev['package_events'],
         'package_pct': round(100 * (cur['package_ms'] - prev['package_ms']) / ms, 1),
         'core_events': cur['core_events'] - prev['core_events'],
         'core_pct': round(100 * (cur['core_ms'] - prev['core_ms']) / ms / max(cur['cpus'], 1), 1)}
    for k in GPU_COUNTERS.values():
        if k in gcur and k in (gprev or {}):
            d[f'gpu_{k}_pct'] = round(100 * (gcur[k] - gprev[k]) / 1000 / ms, 1)
    return d


def gpu():
    q = GPU_Q
    try:
        r = subprocess.run(['nvidia-smi', f'--query-gpu={q}', '--format=csv,noheader,nounits'],
                           capture_output=True, text=True, timeout=20)
        apps = subprocess.run(['nvidia-smi', '--query-compute-apps=pid,process_name,used_memory',
                               '--format=csv,noheader,nounits'], capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired) as e:
        return {'error': str(e)}
    vals = [v.strip() for v in r.stdout.strip().split(',')]
    g = dict(zip(q.split(','), vals))
    g['counters_us'] = gpu_counters()
    g['apps'] = [dict(zip(('pid', 'name', 'mem_mib'), [x.strip() for x in line.split(',')]))
                 for line in apps.stdout.strip().splitlines() if line.strip()]
    return g


def temps():
    out = {}
    for hw in Path('/sys/class/hwmon').glob('hwmon*'):
        name = read(hw / 'name').strip()
        for t in sorted(hw.glob('temp*_input')):
            label = read(t.with_name(t.name.replace('_input', '_label'))).strip() or t.name
            try:
                out[f'{name}/{label}'] = int(read(t).strip()) / 1000
            except ValueError:
                pass
    return out


def cpu_clocks():
    mhz = [float(x) for x in re.findall(r'cpu MHz\s+:\s+([\d.]+)', read('/proc/cpuinfo'))]
    gov = {read(p).strip() for p in Path('/sys/devices/system/cpu').glob('cpu[0-9]*/cpufreq/scaling_governor')}
    epp = {read(p).strip() for p in
           Path('/sys/devices/system/cpu').glob('cpu[0-9]*/cpufreq/energy_performance_preference')}
    return {'mhz_min': min(mhz, default=None), 'mhz_avg': round(sum(mhz) / len(mhz)) if mhz else None,
            'mhz_max': max(mhz, default=None), 'governor': sorted(gov), 'epp': sorted(epp)}


def meminfo():
    m = {k: int(v) // 1024 for k, v in re.findall(r'^(\w+):\s+(\d+) kB', read('/proc/meminfo'), re.M)}
    keep = ('MemTotal', 'MemAvailable', 'MemFree', 'Cached', 'Buffers', 'Dirty', 'Writeback', 'AnonPages', 'Mlocked',
            'Shmem', 'SwapTotal', 'SwapFree', 'AnonHugePages', 'HugePages_Total')
    return {f'{k}_mib': m.get(k) for k in keep}


def pressure():
    out = {}
    for kind in ('cpu', 'memory', 'io'):
        for line in read(f'/proc/pressure/{kind}').splitlines():
            f = dict(x.split('=') for x in line.split()[1:])
            out[f'{kind}_{line.split()[0]}_avg10'] = float(f.get('avg10', 0))
    return out


def disk_free():
    out = {}
    for name, p in (('models', MODELS), ('repo', ROOT)):
        try:
            s = os.statvfs(p)
            out[f'{name}_free_gb'] = round(s.f_bavail * s.f_frsize / 1e9, 1)
        except OSError:
            pass
    return out


class Sampler:
    def __init__(self):
        self.last_t = None
        self.last_procs = {}
        self.last_throttle = None
        self.last_gpu_counters = None

    def snapshot(self, event, lines, full):
        t0 = time.time()
        p0, c0, d0 = proc_times(), cpu_total(), diskstats()
        time.sleep(1.0)
        t1 = time.time()
        p1, c1, d1 = proc_times(), cpu_total(), diskstats()
        dt = t1 - t0
        since = (t1 - self.last_t) if self.last_t else None
        procs = []
        for pid, (ticks, rss, rd, wr) in p1.items():
            a = p0.get(pid)
            cpu1 = round(100 * (ticks - a[0]) / HZ / dt, 1) if a else None
            b = self.last_procs.get(pid)
            cpu_since = round(100 * (ticks - b[0]) / HZ / since, 1) if b and since else None
            rd_since = round((rd - b[2]) / 2**20, 1) if b and since and rd is not None and b[2] is not None else None
            wr_since = round((wr - b[3]) / 2**20, 1) if b and since and wr is not None and b[3] is not None else None
            procs.append((pid, cpu1, cpu_since, rss * PAGE // 2**20, rd_since, wr_since))
        if not full:   # the busy and the large ones
            busy = sorted(procs, key=lambda p: -(p[1] or 0))[:25]
            large = sorted(procs, key=lambda p: -p[3])[:25]
            hot = [p for p in procs if (p[1] or 0) >= 2 or (p[2] or 0) >= 2 or p[3] >= 512 or (p[4] or 0) >= 64]
            keep = {p[0] for p in busy + large + hot}
            procs = [p for p in procs if p[0] in keep]
        rows = []
        for pid, cpu1, cpu_since, rss, rd, wr in sorted(procs, key=lambda p: -(p[1] or 0)):
            info = proc_info(pid)
            if info:
                rows.append({**info, 'cpu_pct_1s': cpu1, 'cpu_pct_since_last': cpu_since, 'rss_mib': rss,
                             'read_mib_since_last': rd, 'write_mib_since_last': wr})
        span = c1['all'] - c0['all'] or 1
        cpu = {k: round(100 * (c1[k] - c0[k]) / span, 1) for k in ('user', 'system', 'idle', 'iowait', 'steal')}
        disks = {k: {'read_mib_s': round((v[0] - d0[k][0]) / 2**20 / dt, 1),
                     'write_mib_s': round((v[1] - d0[k][1]) / 2**20 / dt, 1),
                     'busy_pct': round(100 * (v[2] - d0[k][2]) / 1000 / dt, 1)} for k, v in d1.items() if k in d0}
        g, thr = gpu(), cpu_throttle()
        snap = {'t': now(), 'event': event, 'lines': lines, 'full': full, 'loadavg': read('/proc/loadavg').split()[:3],
                'cpu_pct': cpu, 'cpu_clock': cpu_clocks(), 'mem': meminfo(), 'psi': pressure(), 'disk_io': disks,
                'disk': disk_free(), 'temps': temps(), 'gpu': g, 'cpu_power_limits': cpu_power_limits(),
                'throttle_total': thr, 'throttle_since_last': throttle_delta(
                    t1, self.last_t, thr, self.last_throttle, g.get('counters_us', {}), self.last_gpu_counters),
                'n_procs': len(p1), 'procs': rows, 'took_s': None}
        self.last_throttle, self.last_gpu_counters = thr, g.get('counters_us')
        snap['took_s'] = round(time.time() - t0, 2)
        self.last_t, self.last_procs = t1, p1
        return snap


class ThermalLog:
    """One CSV row every few seconds: the heat and power between the snapshots."""
    COLS = ['t', 'event', 'cpu_pkg_c', 'cpu_core_max_c', 'cpu_core_avg_c', 'cpu_mhz_avg', 'cpu_busy_pct',
            'cpu_pkg_throttle_events', 'cpu_pkg_throttle_pct', 'cpu_core_throttle_pct', 'gpu_c', 'gpu_tlimit_c',
            'gpu_power_avg_w', 'gpu_power_inst_w', 'gpu_power_limit_w', 'gpu_sm_mhz', 'gpu_util_pct', 'gpu_fan_pct',
            'gpu_power_cap_pct', 'gpu_thermal_pct', 'nvme_c']
    Q = 'temperature.gpu,temperature.gpu.tlimit,power.draw.average,power.draw.instant,enforced.power.limit,clocks.sm,' \
        'utilization.gpu,fan.speed'

    def __init__(self, path):
        self.path = path
        self.prev = None
        new = not path.exists()
        self.f = path.open('a')
        if new:
            self.f.write(','.join(self.COLS) + '\n')

    def row(self, event):
        t = time.time()
        temp = temps()
        cores = [v for k, v in temp.items() if k.startswith('coretemp/Core')]
        mhz = [float(x) for x in re.findall(r'cpu MHz\s+:\s+([\d.]+)', read('/proc/cpuinfo'))]
        c, thr, gc = cpu_total(), cpu_throttle(), gpu_counters()
        try:
            r = subprocess.run(['nvidia-smi', f'--query-gpu={self.Q}', '--format=csv,noheader,nounits'],
                               capture_output=True, text=True, timeout=20).stdout.strip().split(',')
        except (OSError, subprocess.TimeoutExpired):
            r = []
        g = [x.strip() for x in r] + [''] * 8
        busy = d = None
        if self.prev:
            pt, pc, pthr, pgc = self.prev
            span = c['all'] - pc['all'] or 1
            busy = round(100 * (1 - (c['idle'] - pc['idle'] + c['iowait'] - pc['iowait']) / span), 1)
            d = throttle_delta(t, pt, thr, pthr, gc, pgc)
        self.prev = (t, c, thr, gc)
        d = d or {}
        thermal = [d.get(f'gpu_{k}_pct') for k in ('sw_thermal', 'hw_thermal')]
        vals = [round(t, 1), event, temp.get('coretemp/Package id 0'), max(cores, default=None),
                round(sum(cores) / len(cores), 1) if cores else None, round(sum(mhz) / len(mhz)) if mhz else None, busy,
                d.get('package_events'), d.get('package_pct'), d.get('core_pct'), *g[:8],
                d.get('gpu_power_cap_pct'), sum(x for x in thermal if x is not None) if any(x is not None for x in thermal)
                else None, temp.get('nvme/Composite')]
        self.f.write(','.join('' if v in (None, 'N/A', '[N/A]') else str(v) for v in vals) + '\n')
        self.f.flush()


# ------------------------------------------------------------------ following the logs

class Follower:
    """New whole lines of a file that may not exist yet; starts at its end unless from_start."""

    def __init__(self, path, from_start=False):
        self.path = path
        self.pos = None if not from_start else 0
        self.buf = ''

    def new_lines(self):
        try:
            size = self.path.stat().st_size
        except OSError:
            return []
        if self.pos is None:
            self.pos = size
        if size < self.pos:
            self.pos = 0
        if size == self.pos:
            return []
        with self.path.open(errors='replace') as f:
            f.seek(self.pos)
            data = f.read()
            self.pos = f.tell()
        data = self.buf + data
        lines = data.split('\n')
        self.buf = lines.pop()
        return lines


def classify(msg):
    for pat, event, full in EVENTS:
        if pat.search(msg):
            return event, full
    return None


def queue_active():
    return subprocess.run(['systemctl', '--user', 'is-active', '--quiet', 'strata-jbench-queue']).returncode == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run-id', required=True)
    ap.add_argument('--every', type=int, default=300, help='seconds between periodic snapshots')
    ap.add_argument('--thermal-every', type=int, default=5, help='seconds between rows of thermal.csv')
    ap.add_argument('--once', action='store_true', help='one snapshot, then exit')
    ap.add_argument('--no-exit', action='store_true', help='keep going when the queue unit is not active')
    ap.add_argument('--env', default=os.environ.get('BENCH_ENV', ''), help='default: the one this hardware matches')
    a = ap.parse_args()
    sys.path.insert(0, str(ROOT / 'scripts'))
    import envs
    run_dir = envs.run_dir(a.env or envs.current(), a.run_id)
    out_dir = run_dir / 'stats'
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / 'snapshots.jsonl.gz'
    sampler = Sampler()

    def write(event, lines, full):
        snap = sampler.snapshot(event, lines, full)
        with gzip.open(out, 'at') as f:   # one gzip member per snapshot: a cut-short last one loses only itself
            f.write(json.dumps(snap, ensure_ascii=False) + '\n')
        (out_dir / 'last.json').write_text(json.dumps(
            {'t': snap['t'], 'event': event, 'took_s': snap['took_s'], 'pid': os.getpid()}) + '\n')

    write('watch-start', [], True)
    if a.once:
        return
    runner = Follower(run_dir / 'runner.log')
    queue = Follower(run_dir / 'queue.log')
    thermal = ThermalLog(out_dir / 'thermal.csv')
    last_event = 'watch-start'
    thermal.row(last_event)
    last_periodic, last_thermal, idle_since = time.time(), time.time(), None
    while True:
        events, full = [], False
        for line in runner.new_lines():
            msg = line.split(' ', 1)[1] if ' ' in line else line
            c = classify(msg)
            if c:
                events.append((c[0], line))
                full = full or c[1]
        for line in queue.new_lines():
            m = QUEUE_LINE.match(line)
            if m:   # the queue's own lines only (the runner's output is in the queue log too)
                events.append(('queue', line))
                full = True
        for kind, line in events:   # the case (or session) the next rows belong to
            m = re.search(r'(?:session (\S+):|^\S+\s+(\S+): \w+ prefill=)', line)
            last_event = f'{kind}:{(m.group(1) or m.group(2)).rstrip(":")}' if m else kind
        if time.time() - last_thermal >= a.thermal_every:
            thermal.row(last_event)
            last_thermal = time.time()
        if events:
            kinds = list(dict.fromkeys(e[0] for e in events))
            write(kinds[0] if len(kinds) == 1 else '+'.join(kinds), [e[1] for e in events], full)
            last_periodic = time.time()
        elif time.time() - last_periodic >= a.every:
            write('periodic', [], False)
            last_periodic = time.time()
        if not a.no_exit and not queue_active():
            idle_since = idle_since or time.time()
            if time.time() - idle_since > 60:   # let the last lines arrive first
                write('watch-end', [], True)
                return
        else:
            idle_since = None
        time.sleep(1)


if __name__ == '__main__':
    main()
