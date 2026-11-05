# 部門（division）

結果は、モデルを**どう動かしたか**で「部門」に分けています。部門が違う結果は混ぜません。
ハードウェアの「環境」（[envs/](../envs/)）とは独立した区分で、部門ごとに環境があります。

*English: results are split into divisions by how the models are driven. "plain" is the models and the engine alone,
called through the engine's API with no agent harness. The agentic divisions (through a harness such as Strata's own
agent features, DeepSeek Harness or opencode) are planned and not measured yet.*

| 部門 | 状態 | 何を測るか |
| --- | --- | --- |
| [`plain`](plain/division.json) | 計測済み | **プレーン（ハーネスなし）**。モデルとエンジンそのものの性能。`strata launch` で立てたエンジンの OpenAI 互換 API（`/v1/chat/completions`）を、[scripts/bench_runner.py](../scripts/bench_runner.py) が直接呼ぶ。tool call は使わない |
| [`strata`](strata/division.json) | 予定 | エージェント: Strata 自身のエージェント機能を通す |
| [`dsh`](dsh/division.json) | 予定 | エージェント: [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness)（dsh）を通す |
| [`opencode`](opencode/division.json) | 予定 | エージェント: opencode を通す |

いま公開している結果は、すべて `plain` です。

## プレーンとエージェントの違い

プレーンは、モデルとエンジンがどれだけ速く、どれだけ正しく答えるかを、余計な層を挟まずに測ります。
エージェントの部門では、実際の使い方に近い条件で、同じエンジンをハーネス越しに使います。ハーネスが足すものの例:

- システムプロンプトと tool の定義
- tool call の出力形式と、その解釈
- tool の結果を返して続ける、何往復ものやり取り
- 毎ターン長い履歴を送り直すこと（Strata のサーバーは、前のプロンプトと共通の部分を再利用する）

エージェントの部門で測る予定のもの:
- プレーンの測定の一部または全部を、ハーネス越しに測り直したもの
- エージェント特有のタスク（tool call を使う課題、何往復もの作業など）

どの Tier をどの部門で測るかは、その部門を始めるときに決めます。

## 置き場所

| 何 | どこ |
| --- | --- |
| 部門の定義 | `divisions/<部門>/division.json`（`status` が `active` の部門だけ計測できる。ほかは `planned`） |
| 計画 | `plan/<部門>/<環境>/` |
| 結果（作業用） | `results/<部門>/<環境>/<RUN_ID>/` |
| 結果（確定・公開） | `published/<部門>/<環境>/<RUN_ID>/` |
| ケース一覧 | `cases/<部門>/<環境>/` |

計測する部門は環境変数 `BENCH_DIVISION` で選びます（省略すると `plain`）。
いまのランナーはエンジンを直接呼ぶ `plain` だけに対応していて、ほかの部門を指定すると計測を始めません。
