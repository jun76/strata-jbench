[日本語](README.md) · [English](README.en.md) · [中文](README.zh.md)

[← 环境一览](../../README.zh.md)

# Strata 基准测试 用例一览: GeForce RTX 5070 · Core Ultra 5 235 · 64 GB RAM · SATA SSD

**部门: 纯模型（无 harness）** — 模型与引擎本身的性能。不经过智能体 harness：由 runner 直接调用 strata launch 启动的引擎的 OpenAI 兼容 API（/v1/chat/completions）。不使用 tool call。 [部门一览](../../../divisions/README.md)

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
| Strata | strata 0.2.11 (build 0.1.57) |

未使用 Strata 桌面应用。用 CLI <code>strata launch --no-tui</code> 在专用端口（18600）启动引擎，由 <code>scripts/bench_runner.py</code> 直接调用其 OpenAI 兼容的 HTTP API（<code>POST /v1/chat/completions</code>，流式）进行测量。只有 Tier 2 是对同一引擎运行 Strata 自带的基准测试 <code>strata bench run --suite standard-v1</code>。

环境 <code>rtx5070-cu5_235-64g-sata</code> · RUN_ID 2026-11-08-gyro-coder 的记录（machine.json）

## 概要

- 用例: 1,034
- 正式测量请求: 3,414
- 引擎启动: 118
- 预估: 39 小时
- 基准模型: qwen IQ3_S （env.json 的 ref，否则为 Strata 针对此 RAM + VRAM 推荐的模型）
- 完成: 794
- 失败: 4


## 各 Tier 明细

| Tier | 内容 | 模型 | 用例 | 请求 | 预估 h | 完成 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| [0](tier-0.zh.md) | 验证测量工具（基准模型 × 启动 3 次、用 Gyro-S 对照作者的数值、确认编程成果的展开） | 2 | 25 | 183 | 1.2 | 24 |
| [1](tier-1.zh.md) | 所有模型的基础速度（decode 5 种 × temperature 3 档，prefill 4K / 32K / 128K）；支持 DFlash2 的模型的 decode 也用 DFlash2 测量 | 11 | 348 | 1,044 | 2.7 | 348 |
| [2](tier-2.zh.md) | 官方 standard-v1（thinking xhigh，temperature 1.0），整个套件 3 次 | 11 | 165 | 495 | 2.3 | 165 |
| [3](tier-3.zh.md) | 推理 effort none / high × 4 题，编程（帆船）仅 high（所有模型） | 11 | 99 | 297 | 8.3 | 88 |
| [4a](tier-4a.zh.md) | 预留上下文的代价（128K / 256K / 1M 下相同的 4K 输入） | 11 | 33 | 99 | 1.1 | 33 |
| [4b](tier-4b.zh.md) | 训练长度内的长文本（32K / 128K / 256K；基准模型、各系列最大的模型、最小的模型） | 4 | 48 | 144 | 2.2 | 24 |
| [4c](tier-4c.zh.md) | 扩展范围的长文本（512K / 1M；基准模型、最小与最大的模型） | 3 | 24 | 72 | 14.0 | 8 |
| [4d](tier-4d.zh.md) | YaRN 的影响（基准模型，相同输入只改设置） | 1 | 16 | 48 | 3.0 | 16 |
| [5](tier-5.zh.md) | 每次只改一个启动选项（基准模型、最大与最小的模型；含自动 tune） | 3 | 276 | 828 | 4.5 | 88 |


## 模型

| family | model | GB | 类别 | 测量的版本（仓库 @ 提交，RUN_ID 的 models.json） |
| --- | --- | ---: | --- | --- |
| qwen | Q2_0 | 67.3 | 原始权重量化（ISTA） | [ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF @ `ed59f92`](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF/tree/ed59f92082b1e93c0e96d60a8b11aab089b52f09) ([2026-11-06-main](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/models.json)) |
| qwen | IQ2_XS | 68.0 | 原始权重量化（ISTA） | [ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF @ `ed59f92`](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF/tree/ed59f92082b1e93c0e96d60a8b11aab089b52f09) ([2026-11-06-main](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/models.json)) |
| qwen | IQ3_XXS | 75.8 | 原始权重量化（ISTA） | [ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF @ `ed59f92`](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF/tree/ed59f92082b1e93c0e96d60a8b11aab089b52f09) ([2026-11-06-main](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/models.json)) |
| qwen | IQ3_S | 83.6 | 原始权重量化（ISTA） | [ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF @ `ed59f92`](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF/tree/ed59f92082b1e93c0e96d60a8b11aab089b52f09) ([2026-11-06-main](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/models.json)) |
| coder | IQ1_M | 58.4 | expert 减半的剪枝版 | [ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-Coder-GGUF @ `5348543`](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-Coder-GGUF/tree/5348543e0147355ac9cbcb031184a3546350988e) ([2026-11-08-gyro-coder](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-08-gyro-coder/models.json)) |
| gyro | Gyro-S | 58.5 | 原始权重量化（trellis） | [agentionai/Qwen3.8-Flash-Next-Gyro-GGUF @ `1ada084`](https://huggingface.co/agentionai/Qwen3.8-Flash-Next-Gyro-GGUF/tree/1ada08422e404aca51ab9df665f089f34c419c6b) ([2026-11-08-gyro-coder](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-08-gyro-coder/models.json)) |
| gyro | Gyro-M | 92.0 | 原始权重量化（trellis） | [agentionai/Qwen3.8-Flash-Next-Gyro-GGUF @ `1ada084`](https://huggingface.co/agentionai/Qwen3.8-Flash-Next-Gyro-GGUF/tree/1ada08422e404aca51ab9df665f089f34c419c6b) ([2026-11-06-main](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/models.json)) |
| unsloth | UD-IQ1_M (v3.1) | 68.0 | 原始权重量化（Unsloth v3.1） | [unsloth/Qwen3.8-Flash-Next-GGUF @ `d962011`](https://huggingface.co/unsloth/Qwen3.8-Flash-Next-GGUF/tree/d96201194f103c906994f283f504209dc8d2a10c) ([2026-11-06-main](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/models.json)) |
| unsloth | UD-Q2_0 (v3.1) | 70.5 | 原始权重量化（Unsloth v3.1） | [unsloth/Qwen3.8-Flash-Next-GGUF @ `d962011`](https://huggingface.co/unsloth/Qwen3.8-Flash-Next-GGUF/tree/d96201194f103c906994f283f504209dc8d2a10c) ([2026-11-06-main](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/models.json)) |
| unsloth | UD-IQ2_XS (v3.1) | 75.8 | 原始权重量化（Unsloth v3.1） | [unsloth/Qwen3.8-Flash-Next-GGUF @ `d962011`](https://huggingface.co/unsloth/Qwen3.8-Flash-Next-GGUF/tree/d96201194f103c906994f283f504209dc8d2a10c) ([2026-11-06-main](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/models.json)) |
| unsloth | UD-Q2_K_XL (v3.1) | 79.6 | 原始权重量化（Unsloth v3.1） | [unsloth/Qwen3.8-Flash-Next-GGUF @ `d962011`](https://huggingface.co/unsloth/Qwen3.8-Flash-Next-GGUF/tree/d96201194f103c906994f283f504209dc8d2a10c) ([2026-11-06-main](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/models.json)) |


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
