[日本語](README.md) · [English](README.en.md) · [中文](README.zh.md)

[← 環境の一覧](../../README.md)

# Strata ベンチ ケース一覧: GeForce RTX 5070 · Core Ultra 5 235 · 64 GB RAM · SATA SSD

**部門: プレーン（ハーネスなし）** — モデルとエンジンそのものの性能。エージェント用のハーネスは通さず、strata launch で立てたエンジンの OpenAI 互換 API（/v1/chat/completions）をランナーが直接呼ぶ。tool call は使わない。 [部門の一覧](../../../divisions/README.md)

Tier ごとにケースの表がある（1行が1ケース）。全パラメータと結果は Tier ごとの CSV（tier-<Tier>.csv）。エビデンス列の RUN_ID は、そのケースの記録（summary.json、送ったリクエスト、応答、成果物）のフォルダ。生成: `scripts/build_cases.py`。

## 実行環境

| | |
| --- | --- |
| GPU | NVIDIA GeForce RTX 5070 (12 GB, PCIe 5.0 x16) · driver 595.99.02 / CUDA 13.2 · 電力上限 250 W（既定 250 W） |
| CPU | Intel Core Ultra 5 235 · 14 コア / 14 スレッド、最大 5.0 GHz · governor powersave · PL1 65 W / PL2 65 W |
| メモリ | 64 GB（DDR5-5600 32 GB × 2、2 チャネル。OS から見えるのは 60.9 GiB） |
| マザーボード | ASUSTeK COMPUTER INC. PRIME Z890-P WIFI |
| モデルの置き場所 | <strong>SanDisk SD9SB8W1 (SATA SSD)</strong> · SATA SSD 接続（読み込みは最大 0.55 GB/s ほどで、NVMe の数分の一）。RAM + VRAM に収まらない重みを読み直すモデルは、この速さで遅くなる |
| OS | Ubuntu 26.04.1 LTS (Linux 7.0.0-42-generic) |
| Strata | strata 0.2.11 (build 0.1.57) |

Strata のデスクトップアプリは使っていない。CLI の <code>strata launch --no-tui</code> でエンジンを専用ポート（18600）に起動し、OpenAI 互換の HTTP API（<code>POST /v1/chat/completions</code>、ストリーミング）を <code>scripts/bench_runner.py</code> から直接呼んで測る。Tier 2 だけは Strata 同梱のベンチ <code>strata bench run --suite standard-v1</code> を同じエンジンに向けて実行する。

環境 <code>rtx5070-cu5_235-64g-sata</code> · RUN_ID 2026-11-09-harbor-gyro-long-t5 の記録（machine.json）

## 概要

- ケース: 1,034
- 本計測リクエスト: 3,414
- エンジン起動: 118
- 見積もり: 39 時間
- 基準モデル: qwen IQ3_S （env.json の ref、なければ Strata がこの RAM + VRAM に勧めるモデル）
- 完了: 1,018
- 失敗: 16


## Tier ごとの内訳

| Tier | 内容 | モデル | ケース | リクエスト | 見積 h | 完了 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| [0](tier-0.md) | 計測器の検証（基準モデル × 起動3回、Gyro-S で作者の値と照合、コーディングの成果物の展開確認） | 2 | 25 | 183 | 1.2 | 25 |
| [1](tier-1.md) | 全モデルの基礎速度（decode 5種 × temperature 3水準、prefill 4K / 32K / 128K）。decode は DFlash2 対応のモデルで DFlash2 でも測る | 11 | 348 | 1,044 | 2.7 | 348 |
| [2](tier-2.md) | 公式 standard-v1（thinking xhigh、temperature 1.0）をスイートごと3回 | 11 | 165 | 495 | 2.3 | 165 |
| [3](tier-3.md) | 推論エフォート none / high × 4問、コーディング（帆船）は high のみ（全モデル） | 11 | 99 | 297 | 8.3 | 99 |
| [4a](tier-4a.md) | 容量の確保コスト（128K / 256K / 1M に同じ 4K 入力） | 11 | 33 | 99 | 1.1 | 33 |
| [4b](tier-4b.md) | 学習範囲の長文（32K / 128K / 256K。基準モデル、系列ごとに最大のモデル、最小のモデル） | 4 | 48 | 144 | 2.2 | 48 |
| [4c](tier-4c.md) | 拡張範囲の長文（512K / 1M。基準モデル、最小と最大のモデル） | 3 | 24 | 72 | 14.0 | 24 |
| [4d](tier-4d.md) | YaRN の影響（基準モデル、同じ入力で設定だけ変える） | 1 | 16 | 48 | 3.0 | 16 |
| [5](tier-5.md) | 起動オプションを1つずつ変える（基準モデル、最大と最小のモデル。自動 tune を含む） | 3 | 276 | 828 | 4.5 | 260 |


## モデル

| family | model | GB | 種別 | 測った版（リポジトリ @ コミット、RUN_ID の models.json） |
| --- | --- | ---: | --- | --- |
| qwen | Q2_0 | 67.3 | 元重みの量子化 (ISTA) | [ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF @ `ed59f92`](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF/tree/ed59f92082b1e93c0e96d60a8b11aab089b52f09) ([2026-11-06-main](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/models.json), [2026-11-09-harbor-gyro-long-t5](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-09-harbor-gyro-long-t5/models.json)) |
| qwen | IQ2_XS | 68.0 | 元重みの量子化 (ISTA) | [ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF @ `ed59f92`](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF/tree/ed59f92082b1e93c0e96d60a8b11aab089b52f09) ([2026-11-06-main](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/models.json), [2026-11-09-harbor-gyro-long-t5](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-09-harbor-gyro-long-t5/models.json)) |
| qwen | IQ3_XXS | 75.8 | 元重みの量子化 (ISTA) | [ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF @ `ed59f92`](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF/tree/ed59f92082b1e93c0e96d60a8b11aab089b52f09) ([2026-11-06-main](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/models.json), [2026-11-09-harbor-gyro-long-t5](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-09-harbor-gyro-long-t5/models.json)) |
| qwen | IQ3_S | 83.6 | 元重みの量子化 (ISTA) | [ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF @ `ed59f92`](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF/tree/ed59f92082b1e93c0e96d60a8b11aab089b52f09) ([2026-11-06-main](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/models.json), [2026-11-09-harbor-gyro-long-t5](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-09-harbor-gyro-long-t5/models.json)) |
| coder | IQ1_M | 58.4 | expert 半減の剪定版 | [ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-Coder-GGUF @ `5348543`](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-Coder-GGUF/tree/5348543e0147355ac9cbcb031184a3546350988e) ([2026-11-08-gyro-coder](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-08-gyro-coder/models.json), [2026-11-09-harbor-gyro-long-t5](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-09-harbor-gyro-long-t5/models.json)) |
| gyro | Gyro-S | 58.5 | 元重みの量子化 (trellis) | [agentionai/Qwen3.8-Flash-Next-Gyro-GGUF @ `1ada084`](https://huggingface.co/agentionai/Qwen3.8-Flash-Next-Gyro-GGUF/tree/1ada08422e404aca51ab9df665f089f34c419c6b) ([2026-11-08-gyro-coder](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-08-gyro-coder/models.json), [2026-11-09-harbor-gyro-long-t5](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-09-harbor-gyro-long-t5/models.json)) |
| gyro | Gyro-M | 92.0 | 元重みの量子化 (trellis) | [agentionai/Qwen3.8-Flash-Next-Gyro-GGUF @ `1ada084`](https://huggingface.co/agentionai/Qwen3.8-Flash-Next-Gyro-GGUF/tree/1ada08422e404aca51ab9df665f089f34c419c6b) ([2026-11-06-main](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/models.json), [2026-11-09-harbor-gyro-long-t5](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-09-harbor-gyro-long-t5/models.json)) |
| unsloth | UD-IQ1_M (v3.1) | 68.0 | 元重みの量子化 (Unsloth v3.1) | [unsloth/Qwen3.8-Flash-Next-GGUF @ `d962011`](https://huggingface.co/unsloth/Qwen3.8-Flash-Next-GGUF/tree/d96201194f103c906994f283f504209dc8d2a10c) ([2026-11-06-main](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/models.json), [2026-11-09-harbor-gyro-long-t5](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-09-harbor-gyro-long-t5/models.json)) |
| unsloth | UD-Q2_0 (v3.1) | 70.5 | 元重みの量子化 (Unsloth v3.1) | [unsloth/Qwen3.8-Flash-Next-GGUF @ `d962011`](https://huggingface.co/unsloth/Qwen3.8-Flash-Next-GGUF/tree/d96201194f103c906994f283f504209dc8d2a10c) ([2026-11-06-main](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/models.json), [2026-11-09-harbor-gyro-long-t5](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-09-harbor-gyro-long-t5/models.json)) |
| unsloth | UD-IQ2_XS (v3.1) | 75.8 | 元重みの量子化 (Unsloth v3.1) | [unsloth/Qwen3.8-Flash-Next-GGUF @ `d962011`](https://huggingface.co/unsloth/Qwen3.8-Flash-Next-GGUF/tree/d96201194f103c906994f283f504209dc8d2a10c) ([2026-11-06-main](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/models.json), [2026-11-09-harbor-gyro-long-t5](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-09-harbor-gyro-long-t5/models.json)) |
| unsloth | UD-Q2_K_XL (v3.1) | 79.6 | 元重みの量子化 (Unsloth v3.1) | [unsloth/Qwen3.8-Flash-Next-GGUF @ `d962011`](https://huggingface.co/unsloth/Qwen3.8-Flash-Next-GGUF/tree/d96201194f103c906994f283f504209dc8d2a10c) ([2026-11-06-main](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/models.json), [2026-11-09-harbor-gyro-long-t5](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-09-harbor-gyro-long-t5/models.json)) |


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
