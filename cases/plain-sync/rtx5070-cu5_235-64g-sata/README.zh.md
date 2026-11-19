[日本語](README.md) · [English](README.en.md) · [中文](README.zh.md)

[← 环境一览](../../README.zh.md)

# Sync-Strata 基准测试 用例一览: GeForce RTX 5070 · Core Ultra 5 235 · 64 GB RAM · SATA SSD

**部门: Sync-Strata** — 直接通过 Sync-Strata 的 OpenAI 兼容 API 测量推理性能，不经过 harness。 [部门一览](../../../divisions/README.md)

每个 Tier 一张用例表（每行一个用例）。全部参数与结果见各 Tier 的 CSV（tier-<Tier>.csv）。证据列中的 RUN_ID 打开该用例的记录（summary.json、发送的请求、响应、成果物）。由 `scripts/build_cases.py` 生成。

## 运行环境

| | |
| --- | --- |
| GPU | NVIDIA GeForce RTX 5070 (12 GB, PCIe 5.0 x16) · driver 595.99.02 / CUDA 13.2 · 功耗上限 250 W（默认 250 W） |
| CPU | Intel Core Ultra 5 235 · 14 核 / 14 线程，最高 5.0 GHz · governor powersave · PL1 65 W / PL2 65 W |
| 内存 | 64 GB（DDR5-5600 32 GB × 2，2 通道；操作系统可见 60.9 GiB） |
| 主板 | ASUSTeK COMPUTER INC. PRIME Z890-P WIFI |
| 模型存放 | <strong>SanDisk SD9SB8W1 (SATA SSD)</strong> · SATA SSD 连接（读取最高约 0.55 GB/s，仅为 NVMe 的几分之一）。放不进 RAM + VRAM 的权重需要重读，模型会因此变慢 |
| OS | Ubuntu 26.04.1 LTS (Linux 7.0.0-42-generic) |
| 推理引擎 | Sync-Strata 0.1.1 |

Tier 1 直接调用 Sync-Strata API，使用 tail skip R10、128K 上下文和 k8v4 KV。

环境 <code>rtx5070-cu5_235-64g-sata</code> · RUN_ID 2026-11-19-sync-r10 的记录（machine.json）

## 概要

- 用例: 54
- 正式测量请求: 162
- 引擎启动: 3
- 预估: 0 小时
- 基准模型: – （env.json 的 ref，否则为 Strata 针对此 RAM + VRAM 推荐的模型）
- 完成: 54
- 失败: 0


## 各 Tier 明细

| Tier | 内容 | 模型 | 用例 | 请求 | 预估 h | 完成 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| [1](tier-1.zh.md) | 所有模型的基础速度（decode 5 种 × temperature 3 档，prefill 4K / 32K / 128K）；支持 DFlash2 的模型的 decode 也用 DFlash2 测量 | 3 | 54 | 162 | 0.2 | 54 |


## 模型

| family | model | GB | 类别 | 测量的版本（仓库 @ 提交，RUN_ID 的 models.json） |
| --- | --- | ---: | --- | --- |
| sync | Sync-XS | 24.12 | Sync-Strata | 无记录 (2026-11-19-sync-r10) |
| sync | Sync-S | 28.14 | Sync-Strata | 无记录 (2026-11-19-sync-r10) |
| sync | Sync-M | 34.59 | Sync-Strata | 无记录 (2026-11-19-sync-r10) |


## 所有用例的共同条件

- 每个用例测 3 次（seed 1 / 2 / 3）。Tier 0 的基准模型含重新启动共 9 次。standard-v1 整个套件运行 3 次。
- 启动：专用 profile 和专用端口，`--vision off --parallel 1 --tune skip --drafting mtp`，其余为 Strata 默认（auto）。表中“启动选项”只写与此不同之处。将 drafter 固定为 MTP，是因为自 0.2.10 起 Auto 会按模型分别选择 DFlash2 或 MTP（DFlash2 在 Tier 1 的 decode 中对支持它的 11 个模型另行测量，不使用 drafter 在 Tier 5 中测量）。
- 同一“启动会话”的用例在一次引擎启动中连续运行（Tier 1、2、3、4a 的 128K 共用一个会话）。记录运行顺序。
- sampling（temperature 以外）：每次都显式指定 top_p 0.95 / top_k 20 / min_p 0 / presence_penalty 0 / repetition_penalty 1.0（仅 Tier 0 的作者条件例外）。
- thinking 每次都显式指定。不指定时，会依次用 Web 界面共享的 Chat 设置 → 启动 config 的值填充（`serve/server.py` 的 effort_default）。
  - off（effort none）：`"reasoning_effort": "none"` 和 `"chat_template_kwargs": {"enable_thinking": false}`
  - on（effort high）：`"reasoning_effort": "xhigh"` 和 `"chat_template_kwargs": {"enable_thinking": true}`，并显式指定 `reasoning_budget_tokens`（输出 cap 的 3/4；cap ≥ 1,024 且省略 budget 时，Strata 的 answer_room 会自动填入相同的值）
  - standard-v1（Tier 2）保持官方设置（xhigh，budget 0）。cap 2,048 的 sanity 中 answer_room 会在 1,536 处结束思考，这一点会记录下来
  - 每个会话开始时保存 `GET /settings`（共享设置应为空）和 `GET /config`，并用 prompt token 数确认 effort 的提示已加入
- 每个会话开始时做 1 次 warm-up（不计入次数）。每个请求带唯一 ID，以免复用 prefix cache（Tier 4 从第 2 题起有意复用）。
- OOM、启动失败、超时、skip 也作为结果保留。


<details><summary>编程用例的成果存放位置</summary>

Tier 0、3 的编程任务是“帆船停靠港口”的场景（英文提示，场景只给出标题，要求以 3D 体素艺术、用单个 HTML 文件回答；全文见 prompts/coding-harbor.json）。无论每个用例的输出形式如何，都按以下结构展开：

```
<run-id>/cases/<case id>/artifact/
  response.md     最终回答全文（thinking 在 requests.jsonl 中）
  files/          从代码块中取出的文件（写了文件名就用该名称，否则用各语言的默认名）
  manifest.json   取出的文件、命名方式、形式（单个 HTML / 需要服务器 / 其他）、有无 README、运行方法
  screenshot.png  仅当能以单个 HTML 或静态服务器打开时。在 headless Chrome 中让页面运行 10 秒后截图
  console.txt     当时的错误（未捕获的异常、console.error、加载失败）；manifest 的 screenshot 还记录是否画出了内容（几乎一种颜色或没有轮廓则为空白）以及页面是否卡死
```

3 次的结果在 `artifact/` 下按 seed 分文件夹（`seed-1/` 等）。

</details>


<details><summary>预估的前提（rtx5090-128g 首次测量的中位数；其他环境在 env.json 的 assume 中覆盖）</summary>

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
