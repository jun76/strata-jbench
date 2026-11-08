<p align="center"><picture>
  <source media="(prefers-color-scheme: dark)" srcset="media/strata-jbench.png">
  <img src="media/strata-jbench-light.png" alt="strata-jbench" width="560">
</picture></p>

**日本語** | [English](README.en.md) | [中文](README.zh.md)

ローカル LLM 推論エンジン Strata で、Qwen3.8-Flash-Next の量子化版・派生版 18 モデルを同じ条件で測った結果です。
計画・計測スクリプト・生の記録も一緒に置いてあり、同じ手順で追試できます。

いま公開しているのは、すべて**プレーン部門**（ハーネスなし）の結果です。エージェント用のハーネスは通さず、モデルとエンジンそのものの性能を測っています。

## 部門: どのハーネスを使ったか

結果は、モデルをどう動かしたかで「部門」に分けています（[divisions/](divisions/README.md)）。

| 部門 | 状態 | 中身 |
| --- | --- | --- |
| プレーン（`plain`） | 計測済み・公開中 | ハーネスなし。`strata launch` で立てたエンジンの OpenAI 互換 API をランナーが直接呼ぶ。tool call は使わない |
| エージェント（`strata`・`dsh`・`opencode`） | 予定 | Strata 自身のエージェント機能、DeepSeek Harness（dsh）、opencode などのハーネスを通す。プレーンの測定の一部または全部と、エージェント特有のタスク（tool call、何往復ものやり取りなど）を測る |

部門が違う結果は混ぜません。実際にエージェントから使ったときの速さは、ハーネスが足すシステムプロンプト・tool の定義・長い履歴の送り直しのぶん、
プレーンの結果とは変わりえます。

## 結果を見る

計測が終わるたびに、この表の一番上に行が足されます。新しい 3 件を表に出し、それより前は表の下に折りたたんでいます。各行の「見る」から次の 3 つを開けます。

| 見る | 中身 |
| --- | --- |
| 📈 グラフ | その RUN の計測が終わった時点の結果をまとめたページ（GitHub Pages）。モデル別の速さ、入力の長さと待ち時間、standard-v1、thinking の有無、コンテキスト長の確保コスト、長文の読解（〜1M token）、起動オプション、計測時の温度・電力・メモリ、モデル別の一覧。全ケースの数値（`summary.csv`）もここから。右上で日本語・English・中文と、ライト・ダークを切り替えられます |
| 📋 ケース一覧 | 同じ時点の、環境ごとの全ケース（GitHub 上の Markdown と CSV）。Tier ごとの表に、ケースの条件・結果・記録へのリンク |
| 📁 エビデンス | その RUN の記録そのもの（送ったリクエスト、返ってきた応答、集計、起動の記録など。中身は「データの置き場所」） |

グラフとケース一覧には、その RUN までに計測した RUN の結果がまとめて載ります。同じ環境で同じケースが複数の RUN_ID にあるときは、名前が後ろに並ぶ RUN_ID の結果を使います。

<!-- published-runs:start (scripts/publish.py writes this list) -->
| 計測完了 | 部門 | 環境 | RUN_ID | Tier | ケース（done / 全体） | 内容 | 見る |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-11-08 17:24 | プレーン（ハーネスなし） | GeForce RTX 5070 · Core Ultra 5 235 · 64 GB RAM · SATA SSD | `2026-11-08-gyro-coder` | 0, 1, 2, 3, 4a | 111 / 111 | gyro Gyro-S と coder IQ1_M を追加で測った（Tier 0〜4a）。2026-11-06-main ではディスクの都合で外していた2モデル | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5070-cu5_235-64g-sata/2026-11-08-gyro-coder/?env=rtx5070-cu5_235-64g-sata "グラフ") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5070-cu5_235-64g-sata/2026-11-08-gyro-coder/cases/plain/rtx5070-cu5_235-64g-sata/README.md "ケース一覧") [📁](published/plain/rtx5070-cu5_235-64g-sata/2026-11-08-gyro-coder/ "エビデンス") |
| 2026-11-08 08:46 | プレーン（ハーネスなし） | GeForce RTX 5070 · Core Ultra 5 235 · 64 GB RAM · SATA SSD | `2026-11-06-main` | 0, 1, 2, 3, 4a, 4b, 4c, 4d, 5 | 719 / 727 | RTX 5070 · Core Ultra 5 235（PL1/PL2 65 W）· 64 GB · SATA SSD での最初の通し計測（Tier 0〜5、9モデル）。SSD からの読み直しに頼っていた Unsloth UD-IQ3_XXS・UD-Q3_K_XL は外した | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/?env=rtx5070-cu5_235-64g-sata "グラフ") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/cases/plain/rtx5070-cu5_235-64g-sata/README.md "ケース一覧") [📁](published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/ "エビデンス") |
| 2026-11-04 22:51 | プレーン（ハーネスなし） | GeForce RTX 5090 · 128 GB RAM | `2026-11-04-long` | 4b, 4c, 4d | 112 / 112 | Tier 4b・4c・4d（長文の読解 32K〜1M と YaRN の点検）。2026-11-03-main では長文の fixture が未作成で省いていたので、青空文庫と Project Gutenberg の日英10作品から長文を作って追加で測った | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5090-128g/2026-11-04-long/?env=rtx5090-128g "グラフ") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5090-128g/2026-11-04-long/cases/plain/rtx5090-128g/README.md "ケース一覧") [📁](published/plain/rtx5090-128g/2026-11-04-long/ "エビデンス") |

<details>
<summary>それより前の RUN（3 件）</summary>

| 計測完了 | 部門 | 環境 | RUN_ID | Tier | ケース（done / 全体） | 内容 | 見る |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-11-04 18:20 | プレーン（ハーネスなし） | GeForce RTX 5090 · 128 GB RAM | `2026-11-04-q8-t3` | 3 | 9 / 9 | unsloth Q8_0 の Tier 3（thinking の有無とゲーム作成）。当初の計画では Q8_0 を Tier 3 から外していたので、計画に足して追加で測った | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5090-128g/2026-11-04-q8-t3/?env=rtx5090-128g "グラフ") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5090-128g/2026-11-04-q8-t3/cases/plain/rtx5090-128g/README.md "ケース一覧") [📁](published/plain/rtx5090-128g/2026-11-04-q8-t3/ "エビデンス") |
| 2026-11-04 15:25 | プレーン（ハーネスなし） | GeForce RTX 5090 · 128 GB RAM | `2026-11-04-iq3s-mtp` | 0, 1, 2, 3, 4a, 5 | 159 / 159 | qwen IQ3_S の測り直し（2026-11-03-main では MTP の draft layer が読み込まれていなかった）。DFlash2 のケースも含めて同じ Tier を流し直した | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5090-128g/2026-11-04-iq3s-mtp/?env=rtx5090-128g "グラフ") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5090-128g/2026-11-04-iq3s-mtp/cases/plain/rtx5090-128g/README.md "ケース一覧") [📁](published/plain/rtx5090-128g/2026-11-04-iq3s-mtp/ "エビデンス") |
| 2026-11-04 10:41 | プレーン（ハーネスなし） | GeForce RTX 5090 · 128 GB RAM | `2026-11-03-main` | 0, 1, 2, 3, 4a, 5 | 1231 / 1231 | 最初の通し計測（Tier 0・1・2・4a・3・5、18モデル）。このうち qwen IQ3_S は MTP が効いていなかったので、ページには 2026-11-04-iq3s-mtp の測り直しを使う | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5090-128g/2026-11-03-main/?env=rtx5090-128g "グラフ") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5090-128g/2026-11-03-main/cases/plain/rtx5090-128g/README.md "ケース一覧") [📁](published/plain/rtx5090-128g/2026-11-03-main/ "エビデンス") |

</details>
<!-- published-runs:end -->

## 何を測ったか

プレーン部門の計測は段階（Tier）に分けています。ケースの定義は [scripts/build_cases.py](scripts/build_cases.py) にあり、各ケースの条件は上の表の「ケース一覧」で見られます。

| Tier | 何を見るか | 対象 |
| --- | --- | --- |
| 0 | 計測そのものが正しいか、ばらつきはどの程度か | 一部のモデル |
| 1 | 各モデルの素の速さ（prefill・decode、文章の種類別、temperature 別、drafter 別） | 全モデル |
| 2 | Strata 同梱のベンチ standard-v1 での速さと sanity の正答 | 全モデル |
| 3 | thinking の有無で、回答までの時間・正答・ゲーム作成の出来がどう変わるか | 全モデル |
| 4 | コンテキスト長の確保コスト（4a）と、実際の長文の処理（4b〜4d、〜1M token） | 4a は全モデル、4b〜4d は代表モデル |
| 5 | 起動オプションを1つずつ変えたときの変化（自動 tune を含む） | 代表3モデル |

どの RUN にどの Tier が入っているかは、上の表の「Tier」の列にあります。

### 測り方

- Strata のデスクトップアプリは使いません。CLI の `strata launch --no-tui` でエンジンを専用ポートに起動し、
  OpenAI 互換の HTTP API（`POST /v1/chat/completions`、ストリーミング）を [scripts/bench_runner.py](scripts/bench_runner.py) から直接呼んで測ります。
  エージェント用のハーネスは通さず、tool の定義も付けません（プレーン部門）。チャットテンプレートとトークナイズは Strata のサーバーが行います。
  Tier 2 だけは、同梱のベンチ `strata bench run --suite standard-v1` を同じエンジンに向けて実行します。
- drafter は、ケースで指定しない限り MTP に固定します（`--drafting mtp --mtp on`）。thinking とサンプリングの設定は、毎回リクエストで明示します。
- 入力は [prompts/](prompts/) の固定プロンプトです（`MANIFEST.json` に SHA-256）。前の応答のキャッシュを使わないよう、各リクエストの先頭に固有の ID を入れています。
- Tier 4b〜4d の長文は、著作権の切れた日英10作品（青空文庫の夏目漱石・島崎藤村・有島武郎・太宰治・宮沢賢治、Project Gutenberg の Melville・Austen・Dickens・Shelley・Doyle）を
  交互に並べた文書です（[prompts/long-sources.json](prompts/long-sources.json) に取得元と底本）。文書の 10 / 50 / 90% に架空の事実を置き、それを問います。
  同じ文書への2問目以降は、文書の部分を prefix cache から読みます。
- 計測中は、ほかの重い処理（ダウンロード、変換、別の推論エンジン）を同時に動かしません。

### 計測環境

ハードウェア構成（GPU と RAM の組み合わせ）ごとに「環境」として分けています。環境が違う結果は混ぜず、グラフのページの上のボタンで切り替えます。
2つ以上の環境に結果があると、同じモデル・同じ条件で並べた「環境の比較」が出ます。
各環境の構成（GPU、CPU、メモリ、ドライバ、Strata の版など）はグラフのページとケース一覧の冒頭にあり、定義は [envs/](envs/) にあります。

## データの置き場所

計測の記録は `published/<部門>/<環境>/<RUN_ID>/` にあります（いまは `published/plain/…` だけ）。

| 何 | どこ |
| --- | --- |
| ケースごとの結果 | `cases/<case id>/summary.json`（集計）、`requests.jsonl`（送ったリクエスト）、`responses/`（応答の本文）、`artifact/`（ゲーム作成などの成果物） |
| 起動ごとの記録 | `sessions/<session>/start-N/`（`strata launch` の出力、エンジンのログ、/settings・/config・/props、telemetry.csv） |
| standard-v1 の出力 | `standard/` |
| 温度・電力の推移 | `stats/thermal.csv`（5秒ごと） |
| マシンの構成 | `machine.json` |
| 測ったモデルの版 | `models.json`（モデルごとの Hugging Face のリポジトリとコミット、ファイルごとのサイズと SHA-256、計測開始時に手元のファイルがその SHA-256 だったか）。同じ名前のモデルでも配布元が更新すると中身が変わるため、どの版を測ったかはこれで分かります。ケース一覧のモデル一覧と、グラフのページの RUN_ID の行からもリンクしています |
| キューとランナーのログ | `queue.log`、`runner.log` |
| その RUN の説明 | `NOTE.md`（上の表の「内容」） |
| 記録どうしの突き合わせ | `verify.json`（エンジンの timings とクライアント側の計時の差、起動の設定がエンジンに入ったか） |
| tune の結果 | `sessions/*-tune-*/start-1/tune-presets.json`。モデルごとのまとめは [configs/tuned/](configs/tuned/) |

ストリームの生データ（SSE と思考の全文）と、PC 上の全プロセスを含むマシンのスナップショットは公開していません。
公開するログでは、ホームフォルダを `~`、ホスト名を `<host>` に置き換えています。

### 手元だけに作られるもの

リポのスクリプトを動かすと、次のフォルダがリポの中に作られます。どれも Git の対象外（[.gitignore](.gitignore)）で、
外へ送られることもありません（ネットワークへ出るのは、モデルのダウンロードだけです）。

| フォルダ | 作るもの | 中身 |
| --- | --- | --- |
| `results/` | `scripts/bench_runner.py` ほか | 計測中の結果。`published/` に移すまでここにあります |
| `results/…/<RUN_ID>/raw/` | `scripts/bench_runner.py` | ストリームの生データ（SSE と思考の全文）。`published/` へは移しません |
| `results/…/<RUN_ID>/stats/snapshots.jsonl.gz`、`last.json` | `scripts/stats_watch.py` | **計測中の PC 全体のスナップショット**。セッション開始・起動・ケース終了・失敗・Tier の切り替わりと 5 分ごとに、動いている全プロセス（PID、ユーザー名、コマンドライン全体、CPU・メモリ・ディスク IO）、GPU を使っているプロセス、CPU・メモリ・PSI・温度を記録します。並走する処理が計測を乱していないか後で確かめるためのもので、他のプログラムのコマンドライン（引数に書いたパスや値を含む）が残るため、`published/` へは移しません |
| `preview/` | `scripts/build_cases.py`、`scripts/build_results.py` | `results/` も読んで作る確認用のグラフとケース一覧 |
| `run-status/` | `scripts/start_pipeline.sh`、`scripts/healthcheck.py`、`scripts/preflight.py` | 無人実行の状態（`STATUS.md`、`ALERTS.log`、`current-run.json`、`preflight.json`） |
| `downloads/` | `scripts/download_models.py`、`scripts/overnight.py` | モデル取得の状態とログ（`manifest.json` に SHA-256） |
| `work/` | `scripts/overnight.py`（NVFP4-QAD の変換） | NVFP4-QAD 変換用の作業フォルダ。長文コーパスの元データ（`work/corpus/raw/`、手で取得）もここに置き、`scripts/long_corpus.py` が読みます |

スナップショットを取りたくないときは、`scripts/start_pipeline.sh` が起動する `strata-jbench-stats` ユニットを止めてください
（`systemctl --user stop strata-jbench-stats`。計測そのものは続きます）。いらなくなったら `results/` の中を消してかまいません。

リポの外では、モデルの重みが `~/.local/share/strata/Strata-data/models` に、Strata の起動プロファイル
（`launch-<model>-<context>`）と Tier 5 の tune のプリセットが Strata の設定に書かれます。計測中は systemd のユーザーユニット
（`strata-jbench-*`、`systemd-run` による一時的なもの）が動きます。

## 追試する

計測は長時間かかるので、systemd のユーザーユニットとして無人で動かします。手順（環境の用意、preflight、開始、監視、異常時の復旧、結果の確定）は
[AGENTS.md](AGENTS.md)（英語）に、環境の定義の書き方は [envs/README.md](envs/README.md) にあります。

前提として、Strata（デスクトップアプリ）を入れて一度モデルをインストールしておくことと、Strata のソースを `~/Strata` に
置いておくことが要ります（取得するファイルとその SHA-256 はソースの `setup.py` が決めます）。ダウンロード用と NVFP4-QAD 変換用の
Python 環境は `scripts/setup_acquire.py` が作り、`scripts/start_pipeline.sh` が自動で呼びます。

```bash
python3 -I scripts/envs.py list                                     # いまのハードウェアに合う環境
python3 -I scripts/build_cases.py                                    # 計画とケース一覧（ケース数と見積もり時間）
python3 scripts/preflight.py --phase all --steps "0,1,2,3,4a,4b,4c,4d,5"      # 始める前の確認
RUN_ID=<run id> STEPS="0 1 2 3 4a 4b 4c 4d 5" scripts/start_pipeline.sh       # 開始
```

## ライセンス

- **コード**（スクリプト、ページのテンプレート、ページ自体のコード）: [MIT License](LICENSE)
- **計測データ**（`published/`・`snapshots/`・`cases/`・`configs/tuned/`、ページ上の数値とグラフ）: [CC BY 4.0](LICENSE-DATA.md)。
  引用するときは「strata-jbench」とこのリポジトリへのリンク、環境と RUN_ID（例: `rtx5090-128g / 2026-11-03-main`）を添えてください。
- **長文の素材**（`prompts/long-corpus.txt` の10作品の本文）: パブリックドメイン。出典と底本は [prompts/long-sources.json](prompts/long-sources.json)。
- モデル・モデル名・Strata は、それぞれの作者のライセンスに従います。

## 参照・謝辞

- **[Strata](https://github.com/Niko1221/Strata)**（Niko1221 and the Strata contributors, MIT License）: 計測に使ったローカル LLM 推論エンジン。Tier 2 の standard-v1 も Strata 同梱のベンチです。
- **[青空文庫](https://www.aozora.gr.jp/)**: 長文の日本語5作品（夏目漱石『吾輩は猫である』、島崎藤村『破戒』、有島武郎『或る女』、太宰治『人間失格』、宮沢賢治『銀河鉄道の夜』）。
  入力・校正をしたボランティアの方々に感謝します。各作品の底本・入力・校正の記載は `prompts/long-sources.json` に残しています。
- **[Project Gutenberg](https://www.gutenberg.org/)**: 長文の英語5作品（Melville, *Moby-Dick*; Austen, *Pride and Prejudice*; Dickens, *A Tale of Two Cities*;
  Shelley, *Frankenstein*; Doyle, *The Adventures of Sherlock Holmes*）。Project Gutenberg の規約に従い、ヘッダー・ライセンス・商標の表記を外した本文だけを使っています。
- **モデル**: Qwen3.8-Flash-Next（Qwen）と、その量子化版・派生版の作者の方々。

| リポジトリ | このベンチでの名前 |
| --- | --- |
| [ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF) | qwen Q2_0, IQ2_XS, IQ3_XXS, IQ3_S |
| [ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-Coder-GGUF](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-Coder-GGUF) | coder IQ1_M |
| [agentionai/Qwen3.8-Flash-Next-Gyro-GGUF](https://huggingface.co/agentionai/Qwen3.8-Flash-Next-Gyro-GGUF) | gyro Gyro-S, Gyro-M |
| [unsloth/Qwen3.8-Flash-Next-GGUF](https://huggingface.co/unsloth/Qwen3.8-Flash-Next-GGUF) | unsloth UD-IQ4_XS, UD-Q4_K_XL, UD-Q5_K_XL, UD-Q6_K_XL, Q8_0 |
| [ukisai/Swift-1.5-Qwen3.8-Flash-Next-GSQ-RCO-GGUF](https://huggingface.co/ukisai/Swift-1.5-Qwen3.8-Flash-Next-GSQ-RCO-GGUF) | swift IQ2_XS, IQ3_XXS, IQ3_S |
| [Maximilian228/Qwen3.8-Flash-Next-NVFP4-GPTQ-Strata](https://huggingface.co/Maximilian228/Qwen3.8-Flash-Next-NVFP4-GPTQ-Strata) | nvfp4 NVFP4 |
| [Maximilian228/Qwen3.8-Flash-Next-NVIDIA-NVFP4-Strata](https://huggingface.co/Maximilian228/Qwen3.8-Flash-Next-NVIDIA-NVFP4-Strata) | nvfp4 NVFP4-NVIDIA |
| [nvidia/Qwen3.8-Flash-Next-FP4-Local](https://huggingface.co/nvidia/Qwen3.8-Flash-Next-FP4-Local) | nvfp4 NVFP4-QAD（FP4 向けの再学習。計測する PC で Strata の変換ツールにより Strata の形式に変換。`scripts/overnight.py` が行う） |
