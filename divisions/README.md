# 部門（division）

結果は、モデルを**どう動かしたか**で「部門」に分けています。部門が違う結果は混ぜません。
ハードウェアの「環境」（[envs/](../envs/)）とは独立した区分で、部門ごとに環境があります。

*English: results are split into divisions by how the models are driven. "plain" is the models and the engine alone,
called through the engine's API with no agent harness. Each agentic division hands the game task (Minecraft) to one
agent harness in one shot, with a recording proxy between the harness and the engine that keeps the engine-side
conditions (sampling, thinking, seed, output cap) the same for every harness.*

| 部門 | 状態 | 何を測るか |
| --- | --- | --- |
| [`plain`](plain/division.json) | 計測済み | **プレーン（ハーネスなし）**。モデルとエンジンそのものの性能。`strata launch` で立てたエンジンの OpenAI 互換 API（`/v1/chat/completions`）を、[scripts/bench_runner.py](../scripts/bench_runner.py) が直接呼ぶ。tool call は使わない。Tier 0〜5 |
| [`dsh`](dsh/division.json) | 計測できる（未計測） | エージェント: [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness)（dsh 0.2.1-rc.5、単体の CLI の headless profile） |
| [`strata`](strata/division.json) | 計測できる（未計測） | エージェント: Strata デスクトップアプリ 0.2.11 のエージェント機能。アプリのエージェントのコード（agent bridge）でチャット1ターンを動かす: アプリが pin した dsh 0.2.1-alpha.3 と、アプリの profile・プラグイン、モード Bypass、thinking High |
| [`opencode`](opencode/division.json) | 計測できる（未計測） | エージェント: opencode 1.19.3（`opencode run`） |
| [`hermes`](hermes/division.json) | 計測できる（未計測） | エージェント: Hermes Agent v0.21.5（タグ 2026.9.24、`hermes chat --oneshot`） |
| [`pi`](pi/division.json) | 計測できる（未計測） | エージェント: pi 0.74.2（`pi --mode json`） |

ハーネスの版は、Strata が `strata connect` で試験した版です（dsh は単体の CLI の版、strata はアプリの版）。どれもゲーム作成（マイクラ）を one shot で渡します。

「計測できる」は `division.json` の `status` が `active` の部門です。`planned` の部門は計測を始めません。
ハーネスの部門は、そのハーネスを入れ、[scripts/harnesses.py](../scripts/harnesses.py) のアダプタを模擬エンジンで動かして確かめてから `active` にします。

## ハーネス部門の測り方

- **ケース**: ゲーム作成（マイクラ、「マイクラ風3D箱庭ゲーム作って」）だけ。形式の指示を足さずに、ハーネスに one shot で渡す（非対話）。各3回。
  プレーンの Tier 3 のゲームは、2026-11-07 から首里城（単一の HTML ファイルで答えるよう指定する英文）です。マイクラはハーネス部門へ移しました（それより前のプレーンの結果はそのまま）。
- **エンジン**: プレーンの基準と同じ起動（コンテキスト 128K、`--vision off --parallel 1 --tune skip --drafting mtp`）。
- **記録プロキシ**（[scripts/agent_proxy.py](../scripts/agent_proxy.py)）: ハーネスはエンジンに直接つながず、ランナーのプロキシを通す。
  プロキシは各リクエストの sampling・thinking・seed・出力 cap をケースの値（プレーンの Tier 3 のゲームと同じ）にそろえ、ハーネスが送った元の値を記録する。
  送らない項目を Strata が共有の Chat 設定や model card で埋めるので、そろえないとハーネスごとに条件が変わってしまうため。
  測る差は、ハーネスが足すもの（system prompt と tool の定義、ターン数、tool の実行、ハーネスの起動）。
- **ハーネスの設定**: 版を固定し（`division.json` の `pin`）、ユーザーの設定とは別のフォルダに作る。窓 131,072 / 出力上限 32,768。自動の compaction とタイトル生成などの副次リクエストは切る。
- **実行**: ケースと seed ごとに使い捨ての作業フォルダを作り、その中で bubblewrap に閉じ込めて動かす（書けるのは作業フォルダとハーネスのフォルダだけ）。tool は承認なしで実行させる。
- **記録**: 終わるまでの壁時計、ハーネスの起動、リクエスト数、tool call、最初のリクエストの入力 token（ハーネスの前置き）、prefix cache の再利用、エンジンが働いていた時間の割合。
  成果物は、作業フォルダに書かれた HTML（なければ回答のコードブロック）から取る。結果のページ（RESULTS）のギャラリーから、sandbox 付きの枠で開ける。

## 置き場所

| 何 | どこ |
| --- | --- |
| 部門の定義 | `divisions/<部門>/division.json`（`status`、`harness`、測るモデル `models`、ハーネスの版 `pin`） |
| 計画 | `plan/<部門>/<環境>/` |
| 結果（作業用） | `results/<部門>/<環境>/<RUN_ID>/`（ハーネスの部門では `harness.json` に使ったハーネスの版と場所） |
| 結果（確定・公開） | `published/<部門>/<環境>/<RUN_ID>/` |
| ケース一覧 | `cases/<部門>/<環境>/` |
| jbench が入れたハーネス | `tools/harness/<部門>/<版>/`（Git 管理外。`scripts/acquire.py fetch harness:<部門>`） |

計測する部門は環境変数 `BENCH_DIVISION` で選びます（省略すると `plain`）。
