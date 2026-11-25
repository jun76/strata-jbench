"""Strata itself, driven by its CLI: `strata launch ... --no-tui --restart` on the bench's port.

The runner's own launch code until the engines got an interface (AGENTS.md 5 has the reasons behind each check).
"""
import json
import os
import re
import shlex
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import catalog  # noqa: E402
import model_files  # noqa: E402
import own_build  # noqa: E402
from engines import Engine  # noqa: E402

# Families whose builds carry their own drafter (catalog "drafter": {"builtin": ...}; also skipped by preflight's MTP
# check), with the --draft value serve gives their engine (serve/hy4_kind.py, serve/inkling_kind.py)
OWN_DRAFTER = {f: b['drafter']['builtin'] for f, b in catalog.by_family().items() if 'builtin' in b['drafter']}


def kill_session(sid):
    """SIGTERM, then SIGKILL after 15 s, every process of session sid (found by /proc, not by name)."""
    def members():
        found = []
        for stat in Path('/proc').glob('[0-9]*/stat'):
            try:
                fields = stat.read_text().rsplit(')', 1)[1].split()
            except OSError:
                continue
            if int(fields[3]) == sid:                     # after "(comm)": state ppid pgrp session
                found.append(int(stat.parent.name))
        return found
    for sig in (15, 9):
        for pid in members():
            try:
                os.kill(pid, sig)
            except OSError:
                pass
        for _ in range(15):
            if not members():
                return
            time.sleep(1)


class Adapter(Engine):
    api_model = 'strata'

    def probe(self):
        try:
            r = subprocess.run(['strata', '--version'], capture_output=True, text=True, timeout=60)
        except (OSError, subprocess.SubprocessError) as e:
            return {'ok': False, 'reason': f'strata is not on PATH ({e})'}
        m = re.match(r'strata (\S+) \(build (\S+);', r.stdout)
        return {'ok': r.returncode == 0, 'version': m.group(1) if m else r.stdout.strip()[:80],
                'build': m.group(2) if m else None, 'where': 'the strata CLI on PATH (the user\'s install)',
                'provision': 'user'}

    def launch_args(self, row):
        opts = row['launch_opts']
        if opts.startswith('configs/'):
            opts = ''
        if '<P コアの論理 CPU>' in opts:
            opts = opts.replace('<P コアの論理 CPU>', self.ctx.get('p_cores') or '')
        fam, model = own_build.target(row['family'], row['model'])   # a build with files of jbench's own: the model Strata knows
        args = ['strata', 'launch', '--family', fam, '--model', model, '--context', str(row['context']),
                '--vision', 'off', '--parallel', '1', '--tune', 'skip', '--access', 'local', '--port', str(self.port),
                '--no-tui', '--restart', '--gpu', str(self.gpu)]
        # The drafter is pinned to MTP: since 0.2.10, Auto picks DFlash2 for some families and MTP for others, which would
        # mix two drafters across the models. Tier 5 changes it with its own --drafting.
        # --mtp on as well: when a launch runs setup (a changed choice), --drafting off makes it pass --mtp off, which saves
        # "mtp": false in the model's installed config (~/.local/share/strata/install/strata-<tag>.json) and drops --mtp from
        # its args; every later launch of that model then ran without the draft layer (qwen IQ3_S in 2026-11-03-main).
        # --mtp on makes such a setup write it back on; a launch that runs no setup cannot, so preflight checks the installed
        # configs and verify checks that the layer loaded.
        # A family with a drafter of its own (Hy4-Flash: DFly2, Inkling-2-Mini: DSpark, built into its builds) has no MTP
        # layer: it starts with its own, Strata's default for it, and only Tier 5's --drafting off changes that.
        if '--drafting' not in opts and row['family'] not in OWN_DRAFTER:
            args += ['--drafting', 'mtp', '--mtp', 'on']
        return args + shlex.split(opts)

    @staticmethod
    def not_applied(args, log):
        """The launch choices the engine's own command line ("engine started: … --serve …" in its log) does not show:
        an unknown --set name only warns, so a setting that never reached the engine would measure the default (AGENTS.md 5)."""
        m = re.search(r'engine started: .*?--serve (.*)', log)
        eng = m.group(1).split() if m else []
        has = lambda flag, value=None: flag in eng and (value is None or (eng.index(flag) + 1 < len(eng) and eng[eng.index(flag) + 1] == value))  # noqa: E731
        want = []
        a = dict(zip(args, args[1:]))   # each flag with the word after it
        want.append(('--max-context', a.get('--context')))
        if a.get('--drafting') == 'off':
            if '--mtp' in eng or '--draft' in eng:
                return ['--drafting off, but the engine has a drafter (--mtp / --draft)']
        elif a.get('--family') in OWN_DRAFTER:
            # its own drafter: serve adds --draft <it> only when the engine says it has one (serve/hy4_kind.py,
            # serve/inkling_kind.py), else starts without it with one log line; a case meant to measure the drafter must not
            # run without
            want.append(('--draft', OWN_DRAFTER[a['--family']]))
        if a.get('--kv'):
            want.append(('--kv', a['--kv']))
        if a.get('--parallel', '1') != '1':
            want.append(('--batch', a['--parallel']))
        if a.get('--pool-cores'):
            want.append(('--pool-cores', a['--pool-cores']))
        if a.get('--vision') == 'gpu':
            want.append(('--vision', None))
        extra = []
        for i, x in enumerate(args):
            if x == '--set' and i + 1 < len(args) and '=' in args[i + 1]:
                k, v = args[i + 1].split('=', 1)
                if (k, v) == ('rope-scaling', 'none'):
                    # launch drops its own --rope-scaling yarn and passes nothing (none is the engine's default): the engine
                    # line must have no other scaling, and the engine says so in its log
                    if (has('--rope-scaling') and not has('--rope-scaling', 'none')) or 'no rope scaling is active' not in log:
                        extra.append('--rope-scaling none')
                    continue
                want.append(('--' + k, v))
        if not eng:
            return ['no "engine started" line in the engine log']
        return [f'{f} {v}' if v is not None else f for f, v in want if not has(f, v)] + extra

    def start(self, row, session_dir):
        args = self.launch_args(row)
        timeout = self.ctx.get('launch_timeout', 3 * 3600)
        t0 = time.time()
        # its own session, so that a launch given up on can be killed with everything it started: the tuner
        # (strata.py tune) outlives the CLI and goes on starting engines, which the next session would launch beside
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True,
                             env=own_build.env(row['family'], row['model']))
        try:
            stdout, stderr = p.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            kill_session(p.pid)
            stdout, stderr = p.communicate()
            (session_dir / 'launch.txt').write_text(shlex.join(args) + '\n\n' + stdout + stderr
                                                    + f'\n[launch timed out after {timeout} s]\n')
            return {'argv': args, 'rc': None, 'launch_s': round(time.time() - t0, 1),
                    'error': f'launch timed out after {timeout} s'}
        (session_dir / 'launch.txt').write_text(shlex.join(args) + '\n\n' + stdout + stderr)
        info = {'argv': args, 'rc': p.returncode, 'launch_s': round(time.time() - t0, 1)}
        if p.returncode != 0 or 'Ready:' not in stdout:
            info['error'] = (stdout + stderr)[-800:]
            return info
        m = re.search(r'Engine log\s+(\S+)', stdout)
        if m and Path(m.group(1)).exists():
            info['engine_log'] = m.group(1)
            # the log is appended to across starts: keep this start's part only (from its last "engine started" line)
            info['engine_log_offset'] = max(0, Path(m.group(1)).read_text(errors='replace').rfind('engine started'))
        return info

    def verify(self, row, info, session_dir):
        if not info.get('engine_log'):
            return True
        args = info['argv']
        text = Path(info['engine_log']).read_text(errors='replace')
        part = text[info['engine_log_offset']:]
        # a build with files of jbench's own: a launch that ran Strata's setup writes the known model's paths back
        mine = own_build.model_file(row['family'], row['model']) if own_build.own(row['family'], row['model']) else None
        if mine and f'--native {mine} ' not in part.split('\n', 1)[0] + ' ':
            info['error'] = f'the engine was not started on {mine} (python3 -I scripts/own_build.py prepare {row["family"]} {row["model"]})'
            info['setting_missing'] = ['own file']
            return False
        # MTP asked for but not loaded: the engine serves (with suffix drafts only), so only its log tells
        if '--drafting' in args and args[args.index('--drafting') + 1] == 'mtp' and 'draft layer loaded' not in part:
            info['error'] = 'MTP asked for (--drafting mtp) but the engine log has no "strata mtp: draft layer loaded"'
            info['mtp_missing'] = True
            return False
        missing = self.not_applied(args, part)
        if missing:
            info['error'] = 'launch choices not in the engine command line: ' + ', '.join(missing)
            info['setting_missing'] = missing
            return False
        return True

    def after_launch(self, row, info, session_dir):
        if '--tune' in row['launch_opts'] and 'skip' not in row['launch_opts']:
            return f'the tuner saved preset(s) {self.save_tune_presets(session_dir, time.time() - info["launch_s"])}'
        return None

    @staticmethod
    def save_tune_presets(session_dir, since):
        """A tune launch (--tune quick / thorough) saves what it found as a Strata preset, active for those choices (the
        desktop app's too). Keep every preset made since this launch began in the session folder: configs/tuned/ is built from
        it (scripts/tuned_configs.py), and the list says which presets the bench added."""
        r = subprocess.run(['strata', 'presets', 'list', '--output', 'json'], capture_output=True, text=True, timeout=120)
        try:
            made = [x for x in json.loads(r.stdout).get('presets', [])
                    if datetime.fromisoformat(x['created']).timestamp() >= since - 5]
        except (ValueError, KeyError, TypeError):
            made = []
        full = []
        for x in made:
            q = subprocess.run(['strata', 'presets', 'show', x['id']], capture_output=True, text=True, timeout=120)
            try:
                full.append({**json.loads(q.stdout), 'active': x.get('active')})
            except ValueError:
                full.append(x)
        (session_dir / 'tune-presets.json').write_text(json.dumps(full, ensure_ascii=False, indent=2) + '\n')
        return [x['name'] for x in made]

    def pid(self):
        out = subprocess.run(['pgrep', '-f', 'strata --serve'], capture_output=True, text=True).stdout.split()
        return int(out[0]) if out else None

    def collect_log(self, info, session_dir):
        if info.get('engine_log'):
            text = Path(info['engine_log']).read_text(errors='replace')
            start = text.rfind('\n', 0, info.get('engine_log_offset', 0)) + 1
            (session_dir / 'engine.log').write_text(text[start:])

    def stop(self, session_dir=None):
        r = subprocess.run(['strata', 'launch', '--stop'], capture_output=True, text=True, timeout=300)
        if session_dir:
            (session_dir / 'stop.txt').write_text(r.stdout + r.stderr)
        for _ in range(60):
            if not subprocess.run(['pgrep', '-f', 'strata --serve'], capture_output=True).stdout:
                return
            time.sleep(2)

    def describe(self, rows):
        return {**self.probe(), 'models_json': model_files.record(self.run_dir) if self.run_dir else None}
