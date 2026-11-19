# Sync-Strata jbench

**日本語** | [English](README.en.md) | [中文](README.zh.md)

ローカル LLM 推論エンジン [Sync-Strata](https://github.com/hiruhiru2005/sync-strata) で、Qwen3.8-Flash-Next の Sync 量子化モデルを測ります。計画、計測スクリプト、計測記録を一緒に置いてあり、同じ手順で追試できます。

## 部門

このブランチは [Sync-Strata のプレーン部門（`plain-sync`）](divisions/README.md) の結果を扱います。ランナーが Sync-Strata の OpenAI 互換 API を直接呼び、モデルとエンジンの性能を測ります。エージェント用のハーネスは通しません。

## 結果を見る

計測が終わった RUN は新しい順に並びます。最新の3件を表に出し、それより前は折りたたんでいます。

| 見る | 中身 |
| --- | --- |
| 📈 グラフ | その RUN が終わった時点の結果を収めた HTML。ダウンロードしてブラウザで開けます。モデル別の速度、入力長と待ち時間、計測時の温度・電力・メモリを確認できます。全ケースの数値を収めた `summary.csv` もリンクされています |
| 📋 ケース一覧 | 環境・Tier ごとの Markdown と CSV。条件、結果、個別の記録へのリンクが載ります |
| 📁 エビデンス | その RUN のリクエスト記録、応答、集計、エンジンの起動記録 |

グラフとケース一覧は、その RUN の終了時点までの結果をまとめています。同じ環境で同じケースを複数回測ったときは、名前が後ろに並ぶ RUN_ID の値を使います。

<!-- published-runs:start (scripts/publish.py writes this list) -->
| 計測完了 | 環境 | RUN_ID | Tier | ケース（done / 全体） | 内容 | 見る |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-11-19 16:39 | GeForce RTX 5070 · Core Ultra 5 235 · 64 GB RAM · SATA SSD | `2026-11-19-sync-r10` | 1 | 54 / 54 | Sync-Strata 0.1.1 で Sync-XS・Sync-S・Sync-M の Tier 1 を R10（tail skip 無効）、128K、KV k8v4、MTP で計測。全54ケース・162リクエスト成功。 | [📈](snapshots/plain-sync/rtx5070-cu5_235-64g-sata/2026-11-19-sync-r10/index.html "グラフ") [📋](https://github.com/jun76/strata-jbench/blob/run/plain-sync/rtx5070-cu5_235-64g-sata/2026-11-19-sync-r10/cases/plain-sync/rtx5070-cu5_235-64g-sata/README.md "ケース一覧") [📁](published/plain-sync/rtx5070-cu5_235-64g-sata/2026-11-19-sync-r10/ "エビデンス") |
<!-- published-runs:end -->

## 何を測ったか

計測を種類ごとに Tier で分けています。各 RUN が測った範囲は結果表の「Tier」列で、サンプリング、tail skip、コンテキスト長などの条件はケース一覧と起動記録で確認できます。ケースの定義は [scripts/build_cases.py](scripts/build_cases.py) にあります。

### 測り方

- [Sync-Strata 対応](scripts/sync_engine.py) が `sync up --api-only` でエンジンを専用ポートに起動します。[ランナー](scripts/bench_runner.py) は `POST /v1/chat/completions` のストリーミング応答を受け取り、入力処理速度（prefill）、生成速度（decode）、最初の文字までの時間（TTFT）を記録します。
- 速度のケースでは、文章・JSON・コード・書き写しなどの短い入力で decode を、長さの違う固定入力で prefill と TTFT を測ります。同じケースを seed 1・2・3 で実行し、中央値と範囲を使います。
- 入力は [prompts/](prompts/) の固定プロンプトです。サンプリングと thinking はリクエストに指定し、先頭に固有の ID を入れて先行リクエストのキャッシュ再利用を避けます。
- 計測用の Sync 設定とプロセス記録は RUN ごとに分け、取得済みモデルを読み込みます。計測中はダウンロードや別の推論エンジンなど、重い処理を同時に動かしません。

### 計測環境

GPU、CPU、RAM、モデルを置くストレージなどの構成ごとに結果を分けています。グラフでは環境を切り替えられ、複数環境で測った同条件の結果は並べて確認できます。ドライバ、電力上限、Sync-Strata の版などは RUN の `machine.json` に記録します。[環境の定義](envs/README.md)

## データの置き場所

| 何 | どこ |
| --- | --- |
| RUN のエビデンス | `published/plain-sync/<環境>/<RUN_ID>/` |
| ケース一覧 | `cases/plain-sync/<環境>/` |
| グラフと集計 CSV | `snapshots/plain-sync/<環境>/<RUN_ID>/` |
| ケースごとの集計と応答 | RUN 内の `cases/<case id>/summary.json`、`requests.jsonl`、`responses/` |
| 起動設定・エンジンログ・テレメトリ | RUN 内の `sessions/<session>/start-N/` |
| 計測機・モデルの配布情報 | `machine.json`、`sync-models.json` |
| 温度・電力の推移 | `stats/thermal.csv` |
| 実行ログと検証結果 | `queue.log`、`runner.log`、`verify.json` |

掲載用のログではホームフォルダを `~`、ホスト名を `<host>` に置き換えます。

### 手元だけに作られるもの

| 何 | どこ |
| --- | --- |
| 実行中・確定前の結果 | `results/` |
| 生のストリームと全文の thinking | 各ケースの `raw/` |
| Sync-Strata の計測用設定・実行状態 | RUN 内の `sync-home/` |
| PC 全体のプロセス・CPU・メモリ・ディスクの記録 | RUN 内の `stats/snapshots.jsonl.gz`。記録を切る場合は `bench.json` に `"stats": false` を指定 |
| 計画、確認用グラフ、進捗・事前チェック | `plan/`、`preview/`、`run-status/` |
| この PC の設定 | ルートの `bench.json` と `envs/<環境>/env.json` |

## 追試する

Sync-Strata をセットアップし、測りたいモデルと共通ファイルを Sync-Strata 側で用意します。現行のアダプタは `~/sync-strata/.sync-local/` にある実行環境とモデル設定を参照します。ハードウェアに一致する環境を [envs/README.md](envs/README.md) に沿って用意し、`bench.json` で RUN_ID と測る範囲を選びます。

```bash
python3 -I scripts/envs.py list          # ハードウェアに合う環境
python3 -I scripts/bench.py config       # 設定と既定値
python3 -I scripts/bench.py plan         # 選んだケースと時間の見積もり
python3 -I scripts/acquire.py check     # モデルと共通ファイルの確認
python3 -I scripts/bench.py start        # supervisor を起動し、事前チェック後に計測
python3 -I scripts/bench.py status       # 進捗
python3 -I scripts/bench.py stop         # 停止。同じ RUN_ID で続きから再開
```

supervisor は端末から切り離されて動きます。事前チェック、監視、復旧、結果確定の手順は [AGENTS.md](AGENTS.md) にあります。

## ライセンス

- コードは [MIT License](LICENSE) です。
- 計測データとグラフは [CC BY 4.0](LICENSE-DATA.md) です。引用時は strata-jbench へのリンク、環境、RUN_ID を添えてください。
- モデルとエンジンは各配布元のライセンスに従います。

## 参照・謝辞

- [Sync-Strata](https://github.com/hiruhiru2005/sync-strata) は計測に使うエンジンと量子化モデルの配布元です。
- [Qwen3.8-Flash-Next](https://huggingface.co/Qwen/Qwen3.8-Flash-Next) は元のモデルです。

| モデル | 配布元 |
| --- | --- |
| Sync-XS | [hiru2005/Sync-XS](https://huggingface.co/hiru2005/Sync-XS) |
| Sync-S | [hiru2005/Sync-S](https://huggingface.co/hiru2005/Sync-S) |
| Sync-M | [sync-strata/Sync-M](https://huggingface.co/sync-strata/Sync-M) |
