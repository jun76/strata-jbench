# envs/ — 計測環境の定義

ベンチを回すハードウェア構成（GPU と RAM の組み合わせ）を「環境」と呼び、1つの環境を `envs/<env>/env.json` で表す。
カードを替えたり RAM を増やしたりしたら、別の環境として足す。同じ PC でも、構成が違えば結果は混ぜない。
環境とは別に、モデルをどう動かしたかの「部門」（[divisions/README.md](../divisions/README.md)、いまは `plain` だけ）があり、場所は部門の下に環境が並ぶ。

| 環境ごとに分かれるもの | 場所 |
| --- | --- |
| 計画（ケースの一覧） | `plan/<division>/<env>/cases.jsonl`・`cases.csv` |
| ケース一覧 | `cases/<division>/<env>/`（Markdown と CSV、入口は `cases/README.md`） |
| 結果 | `results/<division>/<env>/<RUN_ID>/`（作業用、Git 管理外）→ 確定したら `published/<division>/<env>/<RUN_ID>/`（`scripts/publish.py`） |

グラフのページ（RUN を公開するたびにその時点のものを `snapshots/<division>/<env>/<RUN_ID>/` に、確認用は `preview/RESULTS.html`）は全環境を1ページに持ち、環境を切り替えて見る。2つ以上の環境に結果があると、同じモデル・同じ条件で並べた「環境の比較」が出る。

## 環境の決まり方

計測のたびに環境を手で指定するのではなく、いまのハードウェアに合う env.json を `scripts/envs.py` が選ぶ。
合うとみなす条件は `match` の GPU 名が一致し、OS から見える RAM（MemTotal）が `match.ram_gib` の ±3% に入ること。
合う環境が無い、または `--env` / `BENCH_ENV` で指定した環境がハードウェアと合わない場合、preflight とランナーは計測を始めない
（違う構成の結果が別の環境の名前で残るのを防ぐため）。

```bash
python3 -I scripts/envs.py list              # 全環境と、いま合う環境（*）
python3 -I scripts/envs.py detect            # いま合う環境の id
python3 -I scripts/envs.py new rtx5070-64g   # いまのハードウェアから env.json の雛形を作る
```

## env.json の項目

| 項目 | 内容 | 書き方 |
| --- | --- | --- |
| `label` | ページに出す名前 | `"GeForce RTX 5090 · 128 GB RAM"` |
| `match.gpu` | `nvidia-smi` の GPU 名。判定に使う | `new` が入れる |
| `match.ram_gib` | MemTotal（GiB）。判定に使う | `new` が入れる |
| `hardware.gpu_vram_gib`, `hardware.ram_gib` | 見積もりに使う（モデルの大きさを RAM + VRAM と比べた区分 small / edge / large） | `new` が入れる。まだ無い構成の計画を先に作るなら手で書く |
| `gpu_power_limit_w` | 電力上限を設定して測るならその W。preflight が確かめる | `null` ならカードの既定で、確かめない |
| `drafters` | 使える drafter。`dflash2` があると Tier 1 に DFlash2 の decode ケースが付く | `new` が `strata launch --plan` で確かめて入れる |
| `models` | 測るモデル（`"qwen IQ3_S"` の形）。Tier 0・4・5 の代表モデルも、ここに無ければ外れる | `null` なら全18モデル |
| `memory` | RAM の種類・速度・枚数（`sudo dmidecode -t memory` の結果を書き写す） | `{"type": "DDR5", "speed_mts": 5600, "configured_mts": 5600, "modules": [{"slot": "...", "size_gib": 64}], "channels": 2, "recorded_at": "YYYY-MM-DD"}` |
| `assume` | 見積もりの前提の上書き（`scripts/build_cases.py` の `ASSUME` と同じキー） | 遅いカードなら `{"decode_tps": {"small": 40, "edge": 25, "large": 8, "nvfp4": 30}}` など |
| `notes` | 自由記述（電力上限の設定方法など） | |

## 新しい環境を足す手順

[AGENTS.md](../AGENTS.md) の 2.0 を参照。要点:

1. ハードウェアを替えて起動したら `scripts/envs.py new <env>`。
2. `memory`（dmidecode）、`gpu_power_limit_w`、必要なら `models` と `assume` を埋める。
3. GPU の電力上限ユニット（500 W 決め打ち）を、別のカードでは無効化か書き換え。
4. `python3 -I scripts/build_cases.py` → preflight → `test-` の RUN_ID で1ケース → 本番。
