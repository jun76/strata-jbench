#!/usr/bin/env python3
"""Download pinned Strata weights without loading models or changing serving configs."""
import argparse
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import time
from urllib.parse import urlparse


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def write_json(path, value):
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    temp.replace(path)


def build_manifest(s, source, models):
    # Interleave providers first, then complete each provider's documented choices.
    choices = [('qwen', 'Q2_0'), ('gyro', 'Gyro-S'), ('unsloth', 'UD-IQ4_XS'),
               ('qwen', 'IQ2_XS'), ('gyro', 'Gyro-M'),
               ('unsloth', 'UD-Q4_K_XL'), ('qwen', 'IQ3_XXS'), ('coder', 'IQ1_M'),
               ('qwen', 'IQ3_S'),
               ('unsloth', 'UD-Q5_K_XL'), ('unsloth', 'UD-Q6_K_XL'), ('unsloth', 'Q8_0'),
               ('swift', 'IQ2_XS'), ('swift', 'IQ3_XXS'), ('swift', 'IQ3_S'),
               ('nvfp4', 'NVFP4'), ('nvfp4', 'NVFP4-NVIDIA'), ('nvfp4', 'NVFP4-QAD')]
    files = []

    def add(url, destination, family, model):
        pin = s['file_pin'](url)
        if not pin:
            raise ValueError(f'No upstream file pin: {url}')
        files.append({'family': family, 'model': model, 'url': url,
                      'path': str(destination.relative_to(models)), 'bytes': pin[0], 'sha256': pin[1]})

    for family, model in choices:
        if family == 'nvfp4':
            for role, repo, revision, filename, size, sha in s['ready_files'](model):
                add(f'https://huggingface.co/{repo}/resolve/{revision}/{filename}',
                    models / repo.replace('/', '--') / filename, family, model)
            fam = s['FAMILIES'][family]
            add(fam['mmproj_hf'] + fam['mmproj'], models / fam['mmproj'], family, model)
        else:
            fam = s['FAMILIES'][family]
            folder = models / (fam['tag'] + model)
            for i in range(1, s['model_shards'](fam, model) + 1):
                filename = s['model_file'](fam, model, i)
                add(fam['hf'].format(q=model) + filename, folder / filename, family, model)
            add(fam['mmproj_hf'] + fam['mmproj'], models / fam['mmproj'], family, model)
    # Exact same destination (shared encoders / Engram / DSpark) is downloaded once.
    unique = {}
    for f in files:
        if f['path'] in unique and unique[f['path']]['sha256'] != f['sha256']:
            raise ValueError(f'Conflicting path: {f["path"]}')
        unique.setdefault(f['path'], f)
    return {'created_at': now(), 'source_commit': subprocess.check_output(
            ['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip(),
            'source_setup_sha256': hashlib.sha256((source / 'setup.py').read_bytes()).hexdigest(),
            'models_root': str(models), 'choices': choices, 'files': list(unique.values()),
            'scope': '18 Qwen3.8 variants: ISTA 4, Coder 1, Gyro 2, Unsloth 5, Swift 3, NVFP4 3. Excludes Qwen3.6, Orca, DeepSeek. QAD checkpoint download only; conversion separate.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare', 'run'])
    parser.add_argument('--source', type=Path, default=Path.home() / 'Strata')
    parser.add_argument('--models', type=Path, default=Path.home() / '.local/share/strata/Strata-data/models')
    parser.add_argument('--state', type=Path, default=Path(__file__).resolve().parents[1] / 'downloads')
    # Hold a model back for a later run, e.g. until a conversion has freed disk.
    parser.add_argument('--exclude', action='append', default=[], metavar='FAMILY:MODEL')
    args = parser.parse_args()
    args.state.mkdir(parents=True, exist_ok=True)
    lock = (args.state / 'queue.lock').open('w')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    sys.path.insert(0, str(args.source))
    # Download is explicitly authorized. Never allow unpinned or alternate-source fallback.
    os.environ.pop('STRATA_NO_ACQUIRE', None)
    os.environ.pop('STRATA_ALLOW_UNPINNED', None)
    os.environ['STRATA_SOURCE'] = 'huggingface'
    s = runpy.run_path(str(args.source / 'setup.py'), run_name='download_weights_only')
    # ready_fetch normally checks these separately; make its exact upstream pins
    # available to the shared resumable downloader too.
    for repo, meta in s['NVFP4_REPOS'].items():
        s['REPO_PINS'][repo] = {Path(name).name: (size, sha)
                              for name, (role, size, sha) in meta['files'].items()}
    # Hugging Face CLI's saved token is picked up on each HF request. Redirects
    # to signed storage URLs must never carry that token to a different host.
    import urllib.request
    try:
        from huggingface_hub import get_token
    except ImportError:
        def get_token():
            token_file = Path(os.environ.get('HF_TOKEN_PATH', str(Path.home() / '.cache/huggingface/token')))
            return os.environ.get('HF_TOKEN') or (token_file.read_text().strip() if token_file.exists() else None)

    class AuthRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            redirected = super().redirect_request(req, fp, code, msg, headers, newurl)
            if redirected is not None and urlparse(newurl).hostname != 'huggingface.co':
                redirected.remove_header('Authorization')
            return redirected

    opener = urllib.request.build_opener(AuthRedirect())
    def authenticated_open(req, timeout=None):
        s['acquisition'].require('a download')
        if urlparse(req.full_url).hostname == 'huggingface.co':
            token = get_token()
            if token:
                req.add_header('Authorization', 'Bearer ' + token)
        return opener.open(req, timeout=timeout)
    s['download'].__globals__['_urlopen'] = authenticated_open
    manifest_path = args.state / 'manifest.json'
    if args.action == 'prepare':
        manifest = build_manifest(s, args.source, args.models)
        write_json(manifest_path, manifest)
        print(f"Prepared {len(manifest['choices'])} models, {len(manifest['files'])} paths", flush=True)
        return
    manifest = json.loads(manifest_path.read_text())
    if hashlib.sha256((args.source / 'setup.py').read_bytes()).hexdigest() != manifest['source_setup_sha256']:
        raise RuntimeError('setup.py changed after manifest creation; refusing changed download code')
    if Path(manifest['models_root']) != args.models:
        raise RuntimeError('Model directory differs from manifest')
    # Index existing checked Strata files, enabling hardlinks for byte-identical shards.
    pins = {name: (size, sha) for table in s['REPO_PINS'].values() for name, (size, sha) in table.items()}
    checked = {}
    for path in args.models.rglob('*.gguf'):
        pin = pins.get(path.name)
        if pin and path.stat().st_size == pin[0] and s['done'](path):
            checked.setdefault(pin[1], path)
    status = {'pid': os.getpid(), 'started_at': now(), 'state': 'running', 'files': {}}

    def save():
        status['updated_at'] = now()
        write_json(args.state / 'status.json', status)

    save()
    excluded = {tuple(item.split(':', 1)) for item in args.exclude}
    for f in manifest['files']:
        if (f['family'], f['model']) in excluded:
            status['files'][f['path']] = {'state': 'excluded', 'bytes': f['bytes']}
            continue
        dst = args.models / f['path']
        status['current'] = f['path']
        status['files'][f['path']] = {'state': 'downloading', 'started_at': now(), 'bytes': f['bytes']}
        save()
        for attempt in range(1, 4):
            try:
                dst.parent.mkdir(parents=True, exist_ok=True)
                other = checked.get(f['sha256'])
                if not dst.exists() and other and other != dst:
                    # Verify existing source before reusing it, including old .done markers without hashes.
                    s['verify_sha256'](other, f['bytes'], f['sha256'])
                    os.link(other, dst)
                    s['mark'](dst, f"sha256 {f['sha256']}")
                else:
                    part = dst.with_name(dst.name + '.part')
                    allocated = part.stat().st_blocks * 512 if part.exists() else 0
                    remaining = 0 if dst.exists() and s['done'](dst) else max(0, f['bytes'] - allocated)
                    if shutil.disk_usage(args.models).free < remaining + 30_000_000_000:  # 30 GB headroom
                        status['state'] = 'paused_low_disk'
                        save()
                        return
                    s['download'](f['url'], dst, f"{f['family']} {f['model']}: {dst.name}")
                    s['verify_sha256'](dst, f['bytes'], f['sha256'])
                checked[f['sha256']] = dst
                status['files'][f['path']].update(state='verified', completed_at=now(), attempt=attempt)
                save()
                break
            except (Exception, SystemExit) as exc:
                status['files'][f['path']].update(state='failed', error=str(exc), attempt=attempt)
                save()
                if attempt < 3:
                    time.sleep(30)
        # A failed file is preserved in status while the other model downloads continue.
    status['state'] = 'completed_with_errors' if any(f['state'] == 'failed' for f in status['files'].values()) else 'completed'
    status.pop('current', None)
    save()


if __name__ == '__main__':
    main()
