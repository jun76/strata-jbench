<p align="center"><picture>
  <source media="(prefers-color-scheme: dark)" srcset="media/strata-jbench.png">
  <img src="media/strata-jbench-light.png" alt="strata-jbench" width="560">
</picture></p>

**日本語** | [English](README.en.md) | [中文](README.zh.md)

ローカル LLM 推論エンジン [Strata](https://github.com/Niko1221/Strata) とその派生エンジンで、モデルを**同じ物差し**で測るためのベンチと、その結果です。
固定のプロンプトを固定の条件で送り、速さ・待ち時間・正答・成果物を記録します。計画・計測スクリプト・生の記録も一緒に置いてあり、誰でも同じ手順で測れます。

- **何を選ぶとどの数字が取れて、どれだけ時間がかかるか**: [コンフィギュレータ](https://jun76.github.io/strata-jbench/configurator/)（ブラウザで選ぶと、測定条件を 1 つのテキスト「レシピ」にします）
- **自分の PC で測る**: このリポをクローンして、エージェント（Claude Code など）に「strata-jbench で測って」と頼みます。手順は同梱の[スキル](.claude/skills/strata-jbench/SKILL.md)にあります（[追試する](#追試する)）

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
| 2026-11-27 03:55 | プレーン（ハーネスなし） | GeForce RTX 5090 · 128 GB RAM | `2026-11-25-main` | 0, 1, 2, 3, 4a, 4b, 4c, 4d, 5 | 1813 / 1835 | Strata 0.2.21 で全モデル（27 build、Gyro-S v2 と Inkling 2 Mini を含む）の Tier 0〜5 を測り直した（1835 ケース中 1813 完了）。Gyro-S v2 の 256K・1M は jbench が起動できず、NVFP4 の prefill chunk は設定がエンジンに渡らず、Hy4-Flash SQ-128 と Inkling SQ-20 の長文 256K は文書が窓を超えて測れなかった | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5090-128g/2026-11-25-main/?env=rtx5090-128g "グラフ") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5090-128g/2026-11-25-main/cases/plain/rtx5090-128g/README.md "ケース一覧") [📁](published/plain/rtx5090-128g/2026-11-25-main/ "エビデンス") |
| 2026-11-22 15:52 | プレーン（ハーネスなし） | GeForce RTX 5090 · 128 GB RAM | `2026-11-22-hy4` | 1, 2, 3, 4a, 4b | 140 / 147 | Strata 0.2.18 で対応した Tencent Hy4-Flash（SQ-64・SQ-96・SQ-128）を追加して測った（Tier 1〜4b、147 ケース中 140 完了）。1M は起動時に GPU メモリ不足、SQ-128 の 256K は Hy4 のトークナイザで文書が窓を超えて測れなかった | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5090-128g/2026-11-22-hy4/?env=rtx5090-128g "グラフ") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5090-128g/2026-11-22-hy4/cases/plain/rtx5090-128g/README.md "ケース一覧") [📁](published/plain/rtx5090-128g/2026-11-22-hy4/ "エビデンス") |
| 2026-11-19 16:39 | プレーン（ハーネスなし） | GeForce RTX 5070 · Core Ultra 5 235 · 64 GB RAM · SATA SSD | `2026-11-19-sync-r10` | 1 | 54 / 54 | Sync-Strata 0.1.1 で Sync-XS・Sync-S・Sync-M の Tier 1 を R10（tail skip 無効）、128K、KV k8v4、MTP で計測。全54ケース・162リクエスト成功。 | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5070-cu5_235-64g-sata/2026-11-19-sync-r10/?env=rtx5070-cu5_235-64g-sata "グラフ") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5070-cu5_235-64g-sata/2026-11-19-sync-r10/cases/plain/rtx5070-cu5_235-64g-sata/README.md "ケース一覧") [📁](published/plain/rtx5070-cu5_235-64g-sata/2026-11-19-sync-r10/ "エビデンス") |

<details>
<summary>それより前の RUN（8 件）</summary>

| 計測完了 | 部門 | 環境 | RUN_ID | Tier | ケース（done / 全体） | 内容 | 見る |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-11-10 06:23 | プレーン（ハーネスなし） | GeForce RTX 5070 · Core Ultra 5 235 · 64 GB RAM · SATA SSD | `2026-11-09-harbor-gyro-long-t5` | 0, 3, 4b, 4c, 5 | 224 / 236 | まだ測っていなかったケースを測った: 全11モデルのコーディング「港に寄港する帆船」（Tier 0・3）、gyro Gyro-S・Gyro-M と unsloth UD-Q2_K_XL の長文（Tier 4b・4c）、Gyro-S・Gyro-M の起動オプション（Tier 5）。帆船は Tier 3 の33回中16回が描画あり、途中で切れたのは1回。vram-reserve 40%・50% の12ケースは VRAM 12 GB に収まらず起動できなかった | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5070-cu5_235-64g-sata/2026-11-09-harbor-gyro-long-t5/?env=rtx5070-cu5_235-64g-sata "グラフ") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5070-cu5_235-64g-sata/2026-11-09-harbor-gyro-long-t5/cases/plain/rtx5070-cu5_235-64g-sata/README.md "ケース一覧") [📁](published/plain/rtx5070-cu5_235-64g-sata/2026-11-09-harbor-gyro-long-t5/ "エビデンス") |
| 2026-11-09 05:24 | プレーン（ハーネスなし） | GeForce RTX 5090 · 128 GB RAM | `2026-11-09-harbor` | 0, 3 | 21 / 21 | プレーンのコーディングを「港に寄港する帆船」（3D ボクセルアートの単一 HTML、情景は題だけ）に置き換えて測った（Tier 0・3、20モデル）。思考 64K・出力 130,048 で、途中で切れたのは 60 回中 0 回、描画ありは 36 回 | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5090-128g/2026-11-09-harbor/?env=rtx5090-128g "グラフ") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5090-128g/2026-11-09-harbor/cases/plain/rtx5090-128g/README.md "ケース一覧") [📁](published/plain/rtx5090-128g/2026-11-09-harbor/ "エビデンス") |
| 2026-11-08 17:24 | プレーン（ハーネスなし） | GeForce RTX 5070 · Core Ultra 5 235 · 64 GB RAM · SATA SSD | `2026-11-08-gyro-coder` | 0, 1, 2, 3, 4a | 111 / 111 | gyro Gyro-S と coder IQ1_M を追加で測った（Tier 0〜4a）。2026-11-06-main ではディスクの都合で外していた2モデル | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5070-cu5_235-64g-sata/2026-11-08-gyro-coder/?env=rtx5070-cu5_235-64g-sata "グラフ") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5070-cu5_235-64g-sata/2026-11-08-gyro-coder/cases/plain/rtx5070-cu5_235-64g-sata/README.md "ケース一覧") [📁](published/plain/rtx5070-cu5_235-64g-sata/2026-11-08-gyro-coder/ "エビデンス") |
| 2026-11-08 08:46 | プレーン（ハーネスなし） | GeForce RTX 5070 · Core Ultra 5 235 · 64 GB RAM · SATA SSD | `2026-11-06-main` | 0, 1, 2, 3, 4a, 4b, 4c, 4d, 5 | 719 / 727 | RTX 5070 · Core Ultra 5 235（PL1/PL2 65 W）· 64 GB · SATA SSD での最初の通し計測（Tier 0〜5、9モデル）。SSD からの読み直しに頼っていた Unsloth UD-IQ3_XXS・UD-Q3_K_XL は外した | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/?env=rtx5070-cu5_235-64g-sata "グラフ") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/cases/plain/rtx5070-cu5_235-64g-sata/README.md "ケース一覧") [📁](published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/ "エビデンス") |
| 2026-11-04 22:51 | プレーン（ハーネスなし） | GeForce RTX 5090 · 128 GB RAM | `2026-11-04-long` | 4b, 4c, 4d | 112 / 112 | Tier 4b・4c・4d（長文の読解 32K〜1M と YaRN の点検）。2026-11-03-main では長文の fixture が未作成で省いていたので、青空文庫と Project Gutenberg の日英10作品から長文を作って追加で測った | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5090-128g/2026-11-04-long/?env=rtx5090-128g "グラフ") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5090-128g/2026-11-04-long/cases/plain/rtx5090-128g/README.md "ケース一覧") [📁](published/plain/rtx5090-128g/2026-11-04-long/ "エビデンス") |
| 2026-11-04 18:20 | プレーン（ハーネスなし） | GeForce RTX 5090 · 128 GB RAM | `2026-11-04-q8-t3` | 3 | 9 / 9 | unsloth Q8_0 の Tier 3（thinking の有無とコーディング）。当初の計画では Q8_0 を Tier 3 から外していたので、計画に足して追加で測った | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5090-128g/2026-11-04-q8-t3/?env=rtx5090-128g "グラフ") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5090-128g/2026-11-04-q8-t3/cases/plain/rtx5090-128g/README.md "ケース一覧") [📁](published/plain/rtx5090-128g/2026-11-04-q8-t3/ "エビデンス") |
| 2026-11-04 15:25 | プレーン（ハーネスなし） | GeForce RTX 5090 · 128 GB RAM | `2026-11-04-iq3s-mtp` | 0, 1, 2, 3, 4a, 5 | 159 / 159 | qwen IQ3_S の測り直し（2026-11-03-main では MTP の draft layer が読み込まれていなかった）。DFlash2 のケースも含めて同じ Tier を流し直した | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5090-128g/2026-11-04-iq3s-mtp/?env=rtx5090-128g "グラフ") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5090-128g/2026-11-04-iq3s-mtp/cases/plain/rtx5090-128g/README.md "ケース一覧") [📁](published/plain/rtx5090-128g/2026-11-04-iq3s-mtp/ "エビデンス") |
| 2026-11-04 10:41 | プレーン（ハーネスなし） | GeForce RTX 5090 · 128 GB RAM | `2026-11-03-main` | 0, 1, 2, 3, 4a, 5 | 1231 / 1231 | 最初の通し計測（Tier 0・1・2・4a・3・5、18モデル）。このうち qwen IQ3_S は MTP が効いていなかったので、ページには 2026-11-04-iq3s-mtp の測り直しを使う | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5090-128g/2026-11-03-main/?env=rtx5090-128g "グラフ") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5090-128g/2026-11-03-main/cases/plain/rtx5090-128g/README.md "ケース一覧") [📁](published/plain/rtx5090-128g/2026-11-03-main/ "エビデンス") |

</details>
<!-- published-runs:end -->

## 何を測ったか

1 回の計測は、**1 つのエンジン**（本家 Strata、派生エンジン、または起動済みのエンジン）を、**1 つの環境**（その PC のハードウェア）で、選んだ**モデル**と**種目**について測ります。

### 種目

| 種目 | 答える疑問 | 送るもの |
| --- | --- | --- |
| **書く速さ**<br>`speed-decode` | 文章を書く速さは？ | 短い指示を 5 種類送る（日本語の説明文、英語の説明文、JSON、Python のコード、渡した文章の書き写し）。出力は 512 token まで。temperature 0 / 0.7 / 1.0、thinking off で各 3 回。DFlash2 を持つモデルは DFlash2 でももう一度測る。 |
| **読む速さ**<br>`speed-prefill` | 長い入力を読む速さと、最初の 1 文字までの待ち時間は？ | 固定のレコード列を、ちょうど 4K / 32K / 128,000 token になる長さで送る（Strata の standard-v1 と同じ作り方）。出力は 128 token まで。temperature 0.7、thinking off で各 3 回。 |
| **Strata 公式の標準ベンチ**<br>`official-standard` | 本家の標準ベンチ（standard-v1）の値は？ | strata bench run --suite standard-v1 をそのまま 3 回実行する（thinking xhigh、temperature 1.0、性能 9 リクエスト + sanity 12 問）。fixture は Qwen3.8 の tokenizer に合わせてあり、ほかのベースモデルでは token 数が揃わない。 |
| **考えて答える**<br>`think-qa` | 考えさせると、答えるまでの時間と正答はどう変わる？ | 答えを自動で判定できる 4 問（数学、コード（テストを実行して判定）、日本語の推論、英語の推論）を、thinking off と on（xhigh）で解かせる。出力は 16,384 token まで、temperature 1.0 で各 3 回。thinking のないモデルは off だけ。 |
| **1 回の依頼でページを書く**<br>`code-oneshot` | 1 回の依頼で、動くページを書けるか？ | 「港に寄港する帆船」の情景を、3D ボクセルアートの単一 HTML ファイルとして作るよう英文で依頼する。思考 64K、出力はコンテキスト 128K の枠いっぱいまで、temperature 1.0 で 3 回。できたページは headless Chrome で 10 秒動かし、エラー、固まったか、描画されたかを記録する。 |
| **コンテキストを確保するコスト**<br>`context-reserve` | コンテキストを広く確保するだけで遅くなるか？ | コンテキストを 128K / 256K / 1M にして起動し、同じ 4K 入力 + 512 出力を 3 回送る。1M で起動できるかもここで分かる。 |
| **長文の読解**<br>`long-read` | 長い文書を実際に読ませると、速さと正答はどうなる？（〜1M token） | 青空文庫と Project Gutenberg の日英 10 作品から作った文書を、32K / 128K / 256K（学習範囲）と 512K / 1M（拡張範囲）の長さで読ませる。10% / 50% / 90% の位置に埋めた事実を 1 つずつ問い、最後に複数の箇所を組み合わせる問いを出す。各 3 回。対象は代表のモデル。 |
| **YaRN の影響**<br>`yarn-check` | 学習長を超える設定（YaRN）は、同じ入力の結果を変えるか？ | 約 300K の入力を容量 384K（YaRN あり / なし）で、約 200K の入力を容量 256K と 1M で読ませる。基準モデルのみ。 |
| **起動オプションの影響**<br>`launch-options` | どの起動オプションに効果がある？ | 基準の起動から 1 回に 1 つだけ変えて（drafter、draft の深さ、KV 形式、prefill chunk、VRAM の配分、vision、CPU の割り当て、PLE の置き場所、並列、自動 tune）、書く速さ 2 種と読む速さ 2 種を 3 回ずつ測る。対象は代表のモデル。 |
| **計測の点検**<br>`selfcheck` | 計測そのものは正しいか、起動しなおすとどれだけばらつくか？ | 基準モデルで「書く速さ」「読む速さ」を、起動しなおしながら 3 回測る。Gyro-S を作者の公開条件で測って公開値と比べる。コーディングを 1 回実行して成果物の取り出しを確かめる。環境ごとに 1 度。 |
| **エージェントに任せる**<br>`agent-oneshot` | エージェントのハーネスに 1 回で任せると、どれだけ時間がかかり、何ができあがるか？ | 「マイクラ風3D箱庭ゲーム作って」を、形式の指示なしでハーネスに one shot で渡す。思考 32K、出力はコンテキストの枠いっぱいまで、1 回 3,600 秒まで、3 回。sampling・thinking・seed・出力上限は記録プロキシが全ハーネスで同じ値にそろえる。 |

種目は「プリセット」で束ねてあります: `quick`（見出しの速さ 2 つだけ、数分）、`standard`（書く・読む・考えて答える・ページを書く）、`full`（全部）。
種目とケースの対応、各ケースの条件は上の表の「ケース一覧」で見られます（Tier は種目の旧名で、ケース一覧とグラフではまだ併記しています）。定義は [catalog/tasks.json](catalog/tasks.json) と [scripts/case_plan.py](scripts/case_plan.py) にあります。

### 見出しの数字

最初に見る数字は、どれも **1 つの固定の条件**から読みます。複数のケースをまとめた値（平均や中央値の中央値）は見出しにしません。

| 名前 | 定義 |
| --- | --- |
| **JB-decode** 書く速さ | 英語の説明文を書かせたときの decode tok/s。temperature 0.7、thinking off、コンテキスト 128K、drafter はエンジンが自分で選ぶもの（Strata の Auto: DFlash2 を持つモデルは DFlash2、ほかは MTP か内蔵の drafter）、3 回の中央値 |
| **JB-ttft-32k** 32K を読んで最初の 1 文字まで | 32K token の入力を送ってから最初の 1 文字が届くまでの秒数。thinking off、コンテキスト 128K、3 回の中央値 |
| **JB-answer** 考えて答える | 4 問を thinking on で解いたときの正答数（0〜4。3 回中 2 回以上正しければ正答）と、完了までの秒数の中央値。thinking のないモデルは off の値 |
| **JB-page** 1 回で書けたページ | 3 回のうち、エラーなく描画されたページの数（0〜3） |
| **JB-agent** エージェントに任せた結果 | 3 回のうち描画されたゲームの数（0〜3）と、完了までの秒数の中央値 |

文章の種類別・temperature 別・drafter 別などの内訳は、グラフのページに全部あります。指標の定義は [catalog/metrics.json](catalog/metrics.json) に 1 行ずつあります。

### エンジンとモデル

| エンジン | 測り方 |
| --- | --- |
| **Strata** (`strata`) | 本家の Strata。`strata launch` で起動し、指定した設定がエンジンの引数に反映されたかまで照合する。 |
| **Sync-Strata** (`sync-strata`) | Strata のフォーク。Qwen3.8-Flash-Next を独自の量子化 Sync-XS / S / M で動かす（形式は本家と互換なし）。`sync up --api-only` で起動し、設定フォルダは run ごとに分ける。 |
| **OpenAI-compatible endpoint (attach only)** (`endpoint`) | すでに起動してあるエンジンの URL に接続するだけ。jbench は起動も停止もしないので、起動時の設定は検証できない（結果に「接続のみ」と出る）。アダプタのない派生エンジンをまず試すためのもの。 |

速さと引き換えに品質が変わる設定（Sync-Strata の tail skip など）は、既定では切って測ります（`exact`）。エンジンの既定のまま測った結果（`default`）は別扱いで、混ぜません。

モデルはベースモデルごとに [catalog/models/](catalog/models/) にあります: Qwen3.8-Flash-Next（28）、Tencent Hy4-Flash（3）、Thinking Machines Inkling 2 Mini（3）。tokenizer が同じモデルどうしは同じ token 数の入力になるので tok/s をそのまま比べられますが、tokenizer が違うモデルの間では参考値です。

### 同じ物差しであること

- 測定条件は「レシピ」という 1 つのテキストになり、その id（エンジン・設定の系統・動かし方・種目とその版の hash）が結果に付きます。
- ケースごとにも条件の hash が付きます（プロンプトの SHA-256、コンテキスト、起動オプション、thinking、temperature、出力上限、seed）。環境をまたいで並べるのは、この hash が同じケースだけです。
- 頼んだ設定がエンジンに届いたことを確認できなかったケースは、失敗として残します（速さの数字にしません）。

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
| ケースごとの結果 | `cases/<case id>/summary.json`（集計）、`requests.jsonl`（送ったリクエスト）、`responses/`（応答の本文）、`artifact/`（コーディングの成果物） |
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
| `run-status/` | `scripts/bench.py`、`scripts/healthcheck.py`、`scripts/preflight.py` | 無人実行の状態（`STATUS.md`、`ALERTS.log`、`current-run.json`、`preflight.json`） |
| `downloads/` | `scripts/download_models.py`、`scripts/overnight.py` | モデル取得の状態とログ（`manifest.json` に SHA-256） |
| `work/` | `scripts/overnight.py`（NVFP4-QAD の変換） | NVFP4-QAD 変換用の作業フォルダ。長文コーパスの元データ（`work/corpus/raw/`、手で取得）もここに置き、`scripts/long_corpus.py` が読みます |

スナップショットを取りたくないときは、`bench.json` に `"stats": false` と書いてから始めてください。
いらなくなったら `results/` の中を消してかまいません。リポのいちばん上の `bench.json`（計測の設定）も Git の対象外です。

リポの外では、モデルの重みが `~/.local/share/strata/Strata-data/models` に、Strata の起動プロファイル
（`launch-<model>-<context>`）と Tier 5 の tune のプリセットが Strata の設定に書かれます。計測中は、端末から切り離された
見張り役のプロセス（`scripts/supervise.py`）とその子プロセスが動きます。systemd のユニットは作りません。

## 追試する

計測は長時間かかるので、端末から切り離した見張り役のプロセスで無人で動かします（止まったケースの再起動や状態の記録もそのプロセスがします）。

**エージェントに頼む場合**（おすすめ）: このリポをクローンして、Claude Code などのエージェントに「strata-jbench で測って」と頼みます。
リポに同梱の [strata-jbench スキル](.claude/skills/strata-jbench/SKILL.md) が、環境の確認 → コンフィギュレータで選ぶ → 計画と足りないものの確認 → 開始 → 監視 → 結果の確認までを案内します。
足りないエンジン・ハーネス・モデルは、「リポの中の `tools/`（Git 管理外）に取得してよいか、すでにあるなら場所はどこか」を聞いてから用意します。

**手で動かす場合**:

```bash
python3 -I scripts/envs.py list                  # いまのハードウェアに合う環境
python3 -I scripts/build_configurator.py         # preview/configurator.html を作る（ブラウザで開いて選ぶ）
python3 -I scripts/bench.py recipe --apply FILE  # コピーしたレシピを bench.json に入れる
python3 -I scripts/bench.py plan                 # 選んだ範囲のケース数と見積もり時間
python3 -I scripts/acquire.py check              # 足りないもの（モデル、エンジン、ハーネス）
python3 -I scripts/bench.py start                # 確認してから開始（見張り役が端末から切り離されて動く）
python3 -I scripts/bench.py status               # 状況
python3 -I scripts/bench.py stop                 # 止める（同じ run_id でもう一度 start すると続きから）
```

本家 Strata を測るには、Strata（デスクトップアプリ）を入れて一度モデルをインストールしておくことと、Strata のソースを `~/Strata` に置いておくことが要ります（取得するファイルとその SHA-256 はソースの `setup.py` が決めます）。
手順の全体は [AGENTS.md](AGENTS.md) とスキルの [references/](.claude/skills/strata-jbench/references/)（英語）、環境の定義の書き方は [envs/README.md](envs/README.md) にあります。
測った結果を持ち寄るときは、確定した RUN（`published/<部門>/<環境>/<RUN_ID>/`）をプルリクエストで送ってください。

## ライセンス

- **コード**（スクリプト、ページのテンプレート、ページ自体のコード）: [MIT License](LICENSE)
- **計測データ**（`published/`・`snapshots/`・`cases/`・`configs/tuned/`、ページ上の数値とグラフ）: [CC BY 4.0](LICENSE-DATA.md)。
  引用するときは「strata-jbench」とこのリポジトリへのリンク、環境と RUN_ID（例: `rtx5090-128g / 2026-11-03-main`）を添えてください。
- **長文の素材**（`prompts/long-corpus.txt` の10作品の本文）: パブリックドメイン。出典と底本は [prompts/long-sources.json](prompts/long-sources.json)。
- モデル・モデル名・Strata は、それぞれの作者のライセンスに従います。

## 参照・謝辞

- **[Strata](https://github.com/Niko1221/Strata)**（Niko1221 and the Strata contributors, MIT License）: 計測に使ったローカル LLM 推論エンジン。Tier 2 の standard-v1 も Strata 同梱のベンチです。
- **[Sync-Strata](https://github.com/hiruhiru2005/sync-strata)**（hiruhiru2005）: Strata のフォークと、その量子化 Sync-XS / S / M。派生エンジンとして測っています。
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
