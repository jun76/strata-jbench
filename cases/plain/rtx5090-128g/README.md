[日本語](README.md) · [English](README.en.md) · [中文](README.zh.md)

[← 環境の一覧](../../README.md)

# Strata ベンチ ケース一覧: GeForce RTX 5090 · 128 GB RAM

**部門: プレーン（ハーネスなし）** — モデルとエンジンそのものの性能。エージェント用のハーネスは通さず、strata launch で立てたエンジンの OpenAI 互換 API（/v1/chat/completions）をランナーが直接呼ぶ。tool call は使わない。 [部門の一覧](../../../divisions/README.md)

Tier ごとにケースの表がある（1行が1ケース）。全パラメータと結果は Tier ごとの CSV（tier-<Tier>.csv）。エビデンス列の RUN_ID は、そのケースの記録（summary.json、送ったリクエスト、応答、成果物）のフォルダ。生成: `scripts/build_cases.py`。

## 実行環境

| | |
| --- | --- |
| GPU | NVIDIA GeForce RTX 5090 (32 GB, PCIe 5.0 x16) · driver 580.178.04 / CUDA 13.0 · 電力上限 500 W（既定 575 W） |
| CPU | Intel Core i7-14700 · 20 コア / 28 スレッド、最大 5.4 GHz · governor powersave |
| メモリ | 128 GB（DDR5-5600 64 GB × 2、2 チャネル。OS から見えるのは 123.2 GiB） |
| マザーボード | MSI Z790 GAMING PLUS WIFI (MS-7E06) |
| モデルの置き場所 | Fanxiang S880E 2TB (NVMe) |
| OS | Ubuntu 26.10 (Linux 7.3.0-10-generic) |
| Strata | strata 0.2.10 (build 0.1.56) |

Strata のデスクトップアプリは使っていない。CLI の <code>strata launch --no-tui</code> でエンジンを専用ポート（18600）に起動し、OpenAI 互換の HTTP API（<code>POST /v1/chat/completions</code>、ストリーミング）を <code>scripts/bench_runner.py</code> から直接呼んで測る。Tier 2 だけは Strata 同梱のベンチ <code>strata bench run --suite standard-v1</code> を同じエンジンに向けて実行する。

環境 <code>rtx5090-128g</code> · RUN_ID 2026-11-04-q8-t3 の記録（machine.json）

## 概要

- ケース: 1,376
- 本計測リクエスト: 4,566
- エンジン起動: 140
- 見積もり: 34 時間
- 基準モデル: qwen IQ3_S （env.json の ref、なければ Strata がこの RAM + VRAM に勧めるモデル）
- 完了: 1,125
- 失敗: 0


## Tier ごとの内訳

| Tier | 内容 | モデル | ケース | リクエスト | 見積 h | 完了 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| [0](tier-0.md) | 計測器の検証（基準モデル × 起動3回、Gyro-S で作者の値と照合、コーディングの成果物の展開確認） | 2 | 25 | 183 | 0.5 | 24 |
| [1](tier-1.md) | 全モデルの基礎速度（decode 5種 × temperature 3水準、prefill 4K / 32K / 128K）。decode は DFlash2 対応のモデルで DFlash2 でも測る | 18 | 489 | 1,467 | 2.5 | 489 |
| [2](tier-2.md) | 公式 standard-v1（thinking xhigh、temperature 1.0）をスイートごと3回 | 18 | 270 | 810 | 3.0 | 270 |
| [3](tier-3.md) | 推論エフォート none / high × 4問、コーディング（帆船）は high のみ（全モデル） | 18 | 162 | 486 | 8.3 | 144 |
| [4a](tier-4a.md) | 容量の確保コスト（128K / 256K / 1M に同じ 4K 入力） | 18 | 54 | 162 | 1.4 | 54 |
| [4b](tier-4b.md) | 学習範囲の長文（32K / 128K / 256K。基準モデル、系列ごとに最大のモデル、最小のモデル） | 5 | 60 | 180 | 1.8 | 48 |
| [4c](tier-4c.md) | 拡張範囲の長文（512K / 1M。基準モデル、最小と最大のモデル） | 3 | 24 | 72 | 10.2 | 8 |
| [4d](tier-4d.md) | YaRN の影響（基準モデル、同じ入力で設定だけ変える） | 1 | 16 | 48 | 1.1 | 16 |
| [5](tier-5.md) | 起動オプションを1つずつ変える（基準モデル、最大と最小のモデル。自動 tune を含む） | 3 | 276 | 828 | 5.0 | 72 |


## モデル

| family | model | GB | 種別 | 測った版（リポジトリ @ コミット、RUN_ID の models.json） |
| --- | --- | ---: | --- | --- |
| qwen | Q2_0 | 67.3 | 元重みの量子化 (ISTA) | [ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF @ `ed59f92`](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF/tree/ed59f92082b1e93c0e96d60a8b11aab089b52f09) ([2026-11-03-main](../../../published/plain/rtx5090-128g/2026-11-03-main/models.json)) |
| qwen | IQ2_XS | 68.0 | 元重みの量子化 (ISTA) | [ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF @ `ed59f92`](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF/tree/ed59f92082b1e93c0e96d60a8b11aab089b52f09) ([2026-11-03-main](../../../published/plain/rtx5090-128g/2026-11-03-main/models.json)) |
| qwen | IQ3_XXS | 75.8 | 元重みの量子化 (ISTA) | [ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF @ `ed59f92`](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF/tree/ed59f92082b1e93c0e96d60a8b11aab089b52f09) ([2026-11-03-main](../../../published/plain/rtx5090-128g/2026-11-03-main/models.json)) |
| qwen | IQ3_S | 83.6 | 元重みの量子化 (ISTA) | [ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF @ `ed59f92`](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF/tree/ed59f92082b1e93c0e96d60a8b11aab089b52f09) ([2026-11-04-iq3s-mtp](../../../published/plain/rtx5090-128g/2026-11-04-iq3s-mtp/models.json), [2026-11-04-long](../../../published/plain/rtx5090-128g/2026-11-04-long/models.json)) |
| coder | IQ1_M | 58.4 | expert 半減の剪定版 | [ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-Coder-GGUF @ `5348543`](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-Coder-GGUF/tree/5348543e0147355ac9cbcb031184a3546350988e) ([2026-11-03-main](../../../published/plain/rtx5090-128g/2026-11-03-main/models.json)) |
| gyro | Gyro-S | 58.5 | 元重みの量子化 (trellis) | [agentionai/Qwen3.8-Flash-Next-Gyro-GGUF @ `1ada084`](https://huggingface.co/agentionai/Qwen3.8-Flash-Next-Gyro-GGUF/tree/1ada08422e404aca51ab9df665f089f34c419c6b) ([2026-11-03-main](../../../published/plain/rtx5090-128g/2026-11-03-main/models.json)) |
| gyro | Gyro-M | 92.0 | 元重みの量子化 (trellis) | [agentionai/Qwen3.8-Flash-Next-Gyro-GGUF @ `1ada084`](https://huggingface.co/agentionai/Qwen3.8-Flash-Next-Gyro-GGUF/tree/1ada08422e404aca51ab9df665f089f34c419c6b) ([2026-11-03-main](../../../published/plain/rtx5090-128g/2026-11-03-main/models.json), [2026-11-04-long](../../../published/plain/rtx5090-128g/2026-11-04-long/models.json)) |
| unsloth | UD-IQ4_XS (pre-v3.1) | 93.7 | 元重みの量子化 (Unsloth、v3.1 前の版) | [unsloth/Qwen3.8-Flash-Next-GGUF @ `38bb39e`](https://huggingface.co/unsloth/Qwen3.8-Flash-Next-GGUF/tree/38bb39ee97821de2c9009abb7e93950eec396e66) ([2026-11-03-main](../../../published/plain/rtx5090-128g/2026-11-03-main/models.json)) |
| unsloth | UD-Q4_K_XL (pre-v3.1) | 111.3 | 元重みの量子化 (Unsloth、v3.1 でも同じ) | [unsloth/Qwen3.8-Flash-Next-GGUF @ `38bb39e`](https://huggingface.co/unsloth/Qwen3.8-Flash-Next-GGUF/tree/38bb39ee97821de2c9009abb7e93950eec396e66) ([2026-11-03-main](../../../published/plain/rtx5090-128g/2026-11-03-main/models.json)) |
| unsloth | UD-Q5_K_XL | 158.3 | 元重みの量子化 (Unsloth、v3.1 でも同じ) | [unsloth/Qwen3.8-Flash-Next-GGUF @ `38bb39e`](https://huggingface.co/unsloth/Qwen3.8-Flash-Next-GGUF/tree/38bb39ee97821de2c9009abb7e93950eec396e66) ([2026-11-03-main](../../../published/plain/rtx5090-128g/2026-11-03-main/models.json)) |
| unsloth | UD-Q6_K_XL | 169.2 | 元重みの量子化 (Unsloth、v3.1 でも同じ) | [unsloth/Qwen3.8-Flash-Next-GGUF @ `38bb39e`](https://huggingface.co/unsloth/Qwen3.8-Flash-Next-GGUF/tree/38bb39ee97821de2c9009abb7e93950eec396e66) ([2026-11-03-main](../../../published/plain/rtx5090-128g/2026-11-03-main/models.json)) |
| unsloth | Q8_0 | 188.2 | 元重みの量子化 (Unsloth、v3.1 でも同じ)、品質の参照点 | [unsloth/Qwen3.8-Flash-Next-GGUF @ `38bb39e`](https://huggingface.co/unsloth/Qwen3.8-Flash-Next-GGUF/tree/38bb39ee97821de2c9009abb7e93950eec396e66) ([2026-11-03-main](../../../published/plain/rtx5090-128g/2026-11-03-main/models.json), [2026-11-04-long](../../../published/plain/rtx5090-128g/2026-11-04-long/models.json), [2026-11-04-q8-t3](../../../published/plain/rtx5090-128g/2026-11-04-q8-t3/models.json)) |
| swift | IQ2_XS | 69.1 | fine-tune（思考が短い） | [ukisai/Swift-1.5-Qwen3.8-Flash-Next-GSQ-RCO-GGUF @ `99bb8f7`](https://huggingface.co/ukisai/Swift-1.5-Qwen3.8-Flash-Next-GSQ-RCO-GGUF/tree/99bb8f7f95c7aa7b24a36a7786a4f657b30f5d3d) ([2026-11-03-main](../../../published/plain/rtx5090-128g/2026-11-03-main/models.json)) |
| swift | IQ3_XXS | 76.0 | fine-tune（思考が短い） | [ukisai/Swift-1.5-Qwen3.8-Flash-Next-GSQ-RCO-GGUF @ `99bb8f7`](https://huggingface.co/ukisai/Swift-1.5-Qwen3.8-Flash-Next-GSQ-RCO-GGUF/tree/99bb8f7f95c7aa7b24a36a7786a4f657b30f5d3d) ([2026-11-03-main](../../../published/plain/rtx5090-128g/2026-11-03-main/models.json)) |
| swift | IQ3_S | 83.7 | fine-tune（思考が短い） | [ukisai/Swift-1.5-Qwen3.8-Flash-Next-GSQ-RCO-GGUF @ `99bb8f7`](https://huggingface.co/ukisai/Swift-1.5-Qwen3.8-Flash-Next-GSQ-RCO-GGUF/tree/99bb8f7f95c7aa7b24a36a7786a4f657b30f5d3d) ([2026-11-03-main](../../../published/plain/rtx5090-128g/2026-11-03-main/models.json)) |
| nvfp4 | NVFP4 | 128.0 | 元重みの量子化 (GPTQ) | [Maximilian228/Qwen3.8-Flash-Next-NVFP4-GPTQ-Strata @ `640a1db`](https://huggingface.co/Maximilian228/Qwen3.8-Flash-Next-NVFP4-GPTQ-Strata/tree/640a1db97446ddd5e89d2b70ecd0297987192c93) ([2026-11-03-main](../../../published/plain/rtx5090-128g/2026-11-03-main/models.json), [2026-11-04-long](../../../published/plain/rtx5090-128g/2026-11-04-long/models.json)) |
| nvfp4 | NVFP4-NVIDIA | 128.0 | 元重みの量子化 (RTN) | [Maximilian228/Qwen3.8-Flash-Next-NVIDIA-NVFP4-Strata @ `cca8f7f`](https://huggingface.co/Maximilian228/Qwen3.8-Flash-Next-NVIDIA-NVFP4-Strata/tree/cca8f7fee5ce0af932097340a75e06df25c4e57d) ([2026-11-03-main](../../../published/plain/rtx5090-128g/2026-11-03-main/models.json)) |
| nvfp4 | NVFP4-QAD | 102.3 | FP4 向け再学習版 | [nvidia/Qwen3.8-Flash-Next-FP4-Local @ `b9ce18a`](https://huggingface.co/nvidia/Qwen3.8-Flash-Next-FP4-Local/tree/b9ce18a6887e18c089fdea8509a33e63429a3300) ([2026-11-03-main](../../../published/plain/rtx5090-128g/2026-11-03-main/models.json)) |


## 全ケース共通の条件

- どのケースも3回測る（seed 1 / 2 / 3）。Tier 0 の基準モデルは起動しなおしを含めて9回。standard-v1 はスイート全体を3回実行する。
- 起動: 専用プロファイル・専用ポート、`--vision off --parallel 1 --tune skip --drafting mtp`、そのほかは Strata の既定（auto）。表の「起動オプションの差分」はこれとの差だけを書く。drafter を MTP に固定するのは、0.2.10 から Auto がモデルによって DFlash2 と MTP を選び分けるため（DFlash2 は Tier 1 の decode を対応する11モデルで測り直し、drafter なしは Tier 5 で測る）。
- 同じ「起動セッション」のケースは、エンジンを1回起動したまま続けて回す（Tier 1・2・3・4a の 128K は同じセッション）。実行順は記録する。
- sampling（temperature 以外）: top_p 0.95 / top_k 20 / min_p 0 / presence_penalty 0 / repetition_penalty 1.0 を毎回明示する（Tier 0 の作者条件だけ例外）。
- thinking は毎回明示する。指定しないと、Web 画面で共有された Chat 設定 → 起動 config の値で埋まるため（`serve/server.py` の effort_default）。
  - off（effort none）: `"reasoning_effort": "none"` と `"chat_template_kwargs": {"enable_thinking": false}`
  - on（effort high）: `"reasoning_effort": "xhigh"` と `"chat_template_kwargs": {"enable_thinking": true}`、`reasoning_budget_tokens` も明示（出力 cap の 3/4。cap ≥ 1,024 で budget を省くと Strata の answer_room が同じ値を自動で入れる）
  - standard-v1（Tier 2）は公式の指定（xhigh、budget 0）のまま。cap 2,048 の sanity では answer_room により思考が 1,536 で閉じられる点を記録する
  - 各セッションの最初に `GET /settings`（共有設定が空であること）と `GET /config` を保存し、prompt token 数で effort の文が入ったかを確かめる
- 各セッションの最初に warm-up を1回（回数には含めない）。prefix cache の再利用を避けるため各リクエストに固有 ID を入れる（Tier 4 の2問目以降は意図的に再利用する）。
- OOM・起動失敗・timeout・skip も結果として残す。


<details><summary>コーディングのケースの成果物の置き場所</summary>

Tier 0・3 のコーディングは「港に寄港する帆船」の情景（英文のプロンプトで、情景は題だけを示し、3D ボクセルアートで、単一の HTML ファイルで答えるよう指定する。全文は prompts/coding-harbor.json）。出力の形がケースごとに違っても、必ず次の形に展開する。

```
<run-id>/cases/<case id>/artifact/
  response.md     最終回答の全文（thinking は requests.jsonl 側）
  files/          コードブロックから取り出したファイル（ファイル名が書かれていればその名前、なければ言語ごとの既定名）
  manifest.json   取り出したファイル、名前の決め方、形式（単体 HTML / 要サーバー / その他）、README の有無、起動方法
  screenshot.png  単体 HTML か静的サーバーで開けた場合のみ。headless Chrome でページを 10 秒動かしてから撮る
  console.txt     そのときのエラー（捕まえられなかった例外、console.error、読み込みの失敗）。manifest の screenshot に、描画されたか（ほぼ一色・輪郭なしなら空白）と、固まったかも残る
```

3回分は `artifact/` の下に seed ごとのフォルダ（`seed-1/` など）で分ける。

</details>


<details><summary>見積もりの前提（rtx5090-128g の初回の計測の中央値。ほかの環境は env.json の assume で上書き）</summary>

```json
{
  "decode_tps": {
    "small": 240,
    "edge": 100,
    "large": 80,
    "nvfp4": 165
  },
  "prefill_tps": [
    [
      8192,
      3200
    ],
    [
      65536,
      5700
    ],
    [
      262144,
      6000
    ],
    [
      null,
      2500
    ]
  ],
  "prefill_factor": {
    "edge": 0.4,
    "large": 0.35,
    "nvfp4": 0.6
  },
  "launch_base_s": 20,
  "launch_s_per_gb": 0.45,
  "launch_extra_s": {
    "edge": 60
  },
  "tune_s_per_gb": {
    "quick": 4.5,
    "thorough": 20
  },
  "warmup_s": 8,
  "request_overhead_s": 0.2,
  "reasoning_tokens": {
    "none": 0,
    "low": 50,
    "medium": 100,
    "high": 150,
    "xhigh": 200
  },
  "game_reasoning_tokens": {
    "none": 0,
    "low": 3000,
    "medium": 6000,
    "high": 66000
  },
  "game_answer_tokens": 20000,
  "task_answer_tokens": 550,
  "long_answer_tokens": 150,
  "sanity_output_tokens": 150,
  "standard_runs": 3,
  "long_cached_tokens": 16384,
  "standard_run_overhead_s": 60
}
```

</details>
