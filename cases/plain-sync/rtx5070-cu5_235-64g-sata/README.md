[日本語](README.md) · [English](README.en.md) · [中文](README.zh.md)

[← 環境の一覧](../../README.md)

# Sync-Strata ベンチ ケース一覧: GeForce RTX 5070 · Core Ultra 5 235 · 64 GB RAM · SATA SSD

**部門: Sync-Strata** — ハーネスを通さず、Sync-Strata の OpenAI 互換 API を直接呼んで推論性能を測る。 [部門の一覧](../../../divisions/README.md)

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
| 推論エンジン | Sync-Strata 0.1.1 |

Sync-Strata の API を直接呼ぶ。Tier 1 を tail skip R10、128K、KV k8v4 で計測する。

環境 <code>rtx5070-cu5_235-64g-sata</code> · RUN_ID 2026-11-19-sync-r10 の記録（machine.json）

## 概要

- ケース: 54
- 本計測リクエスト: 162
- エンジン起動: 3
- 見積もり: 0 時間
- 基準モデル: – （env.json の ref、なければ Strata がこの RAM + VRAM に勧めるモデル）
- 完了: 54
- 失敗: 0


## Tier ごとの内訳

| Tier | 内容 | モデル | ケース | リクエスト | 見積 h | 完了 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| [1](tier-1.md) | 全モデルの基礎速度（decode 5種 × temperature 3水準、prefill 4K / 32K / 128K）。decode は DFlash2 対応のモデルで DFlash2 でも測る | 3 | 54 | 162 | 0.2 | 54 |


## モデル

| family | model | GB | 種別 | 測った版（リポジトリ @ コミット、RUN_ID の models.json） |
| --- | --- | ---: | --- | --- |
| sync | Sync-XS | 24.12 | Sync-Strata | 記録なし (2026-11-19-sync-r10) |
| sync | Sync-S | 28.14 | Sync-Strata | 記録なし (2026-11-19-sync-r10) |
| sync | Sync-M | 34.59 | Sync-Strata | 記録なし (2026-11-19-sync-r10) |


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
