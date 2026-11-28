<p align="center"><picture>
  <source media="(prefers-color-scheme: dark)" srcset="media/strata-jbench.png">
  <img src="media/strata-jbench-light.png" alt="strata-jbench" width="560">
</picture></p>

[日本語](README.md) | [English](README.en.md) | **中文**

用**同一把尺子**测量本地 LLM 推理引擎 [Strata](https://github.com/Niko1221/Strata) 及其衍生引擎上各模型的基准测试及其结果。
以固定条件发送固定提示词，记录速度、等待时间、正确率和生成的页面。计划、测量脚本和原始记录也一并放在这里，任何人都可以按同样的步骤测量。

- **选什么能得到哪些数字、需要多久**：[配置器](https://jun76.github.io/strata-jbench/configurator/)（在浏览器中选择，它会把测量条件写成一段文本，即“配方”）
- **在自己的电脑上测量**：克隆本仓库，让智能体（如 Claude Code）“用 strata-jbench 测量”。步骤在随仓库附带的[技能](.claude/skills/strata-jbench/SKILL.md)中（见[复现](#复现)）

目前公开的全部是**纯模型部门**（无 harness）的结果：不经过智能体 harness，测量模型与引擎本身的性能。

## 部门：用了哪个 harness

结果按模型的驱动方式分为不同的“部门”（[divisions/](divisions/README.md)）。

| 部门 | 状态 | 内容 |
| --- | --- | --- |
| 纯模型（`plain`） | 已测量、已公开 | 无 harness。由 runner 直接调用 `strata launch` 启动的引擎的 OpenAI 兼容 API。不使用 tool call |
| 智能体（`strata`、`dsh`、`opencode`） | 计划中 | 通过 Strata 自带的智能体功能、DeepSeek Harness（dsh）、opencode 等 harness：测量纯模型部门的部分或全部项目，以及智能体特有的任务（tool call、多轮往返等） |

不同部门的结果不会混在一起。实际从智能体使用时，由于 harness 追加的系统提示、tool 定义和长历史的重复发送，速度可能与纯模型的结果不同。

## 查看结果

每次测量结束，本表最上方就会增加一行。表中显示最新的 3 个，更早的折叠在表的下方。每行的“查看”可打开以下 3 项：

| 查看 | 内容 |
| --- | --- |
| 📈 图表 | 该 RUN 测量结束时的结果汇总页面（GitHub Pages）：各模型速度、输入长度与等待时间、standard-v1、有无 thinking、预留上下文长度的代价、长文阅读（至 1M token）、启动选项、测量时的温度・功耗・内存、各模型一览。全部用例的数值（`summary.csv`）也从这里链接。右上角可切换日本語・English・中文，以及浅色・深色 |
| 📋 用例一览 | 同一时点各环境的全部用例（GitHub 上的 Markdown 与 CSV）：每个 Tier 一张表，含用例的条件、结果和记录的链接 |
| 📁 证据 | 该 RUN 的记录本身（所发请求、所得回答、汇总、启动记录等；见“数据位置”） |

图表和用例一览汇总了截至该 RUN 测量的所有 RUN 的结果。同一环境中同一用例出现在多个 RUN_ID 时，使用名称排在最后的 RUN_ID 的结果。

<!-- published-runs:start (scripts/publish.py writes this list) -->
| 测量完成 | 部门 | 引擎 | 环境 | RUN_ID | Tier | 用例（done / 全部） | 内容 | 查看 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-11-28 12:50 | 纯模型（无 harness） | Strata | GeForce RTX 5090 · 128 GB RAM | `2026-11-28-inkling` | 1, 2, 3, 4a, 4b | 280 / 320 | 在 Strata 0.2.23（Inkling 引擎 0.1.70）上以 DFlash 2 测量 Inkling-2-Mini 的 7 个构建（Tier 1、2、3、4a、4b，320 个用例完成 280 个）。SQ-20 为 0.2.23 起的文件（SQ-20-v2），GSQ-RCO 为 IQ3_S、IQ3_XXS、Q2_K_XL、IQ2_S。40 个失败中，36 个是 SQ-10、SQ-15、SQ-20-v2、IQ3_XXS 在读取 128K prefill 时引擎因 GPU 错误终止（RTX 50 fast mode 的 prefill 注意力缺陷，Niko1221/Strata#7368）及同一会话中受牵连的用例，4 个是 256K 长文档超出上下文 | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5090-128g/2026-11-28-inkling/?env=rtx5090-128g "图表") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5090-128g/2026-11-28-inkling/cases/plain/rtx5090-128g/README.zh.md "用例一览") [📁](published/plain/rtx5090-128g/2026-11-28-inkling/ "证据") |
| 2026-11-27 19:02 | 纯模型（无 harness） | Strata | GeForce RTX 5090 · 128 GB RAM | `2026-11-27-inkling` | 3 | 15 / 15 | 以开启思考的方式测量了 Inkling-2-Mini（SQ-10 / 15 / 20）的 Tier 3（完成 15 个）。Strata 0.2.21 接受 Inkling 的思考级别，因此按与其他模型相同的条件加入了 math-1、code-1、reason-ja-1、reason-en-1、coding-harbor 的 high 用例。关闭思考测量的 coding-harbor 已从计划中移除 | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5090-128g/2026-11-27-inkling/?env=rtx5090-128g "图表") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5090-128g/2026-11-27-inkling/cases/plain/rtx5090-128g/README.zh.md "用例一览") [📁](published/plain/rtx5090-128g/2026-11-27-inkling/ "证据") |
| 2026-11-27 12:19 | 纯模型（无 harness） | Sync-Strata | GeForce RTX 5090 · 128 GB RAM | `2026-11-27-sync` | 1, 3, 4a | 58 / 58 | 在 Sync-Strata 0.1.4 上以 R10（关闭 tail skip）测量 Sync-S 与 Sync-M 的 Tier 1・3・4a（完成 58 个用例）。未测 Sync-XS：在此环境下 Sync-Strata 0.1.4 的启动器把 RAM 预算算成 0.0 GiB，引擎无法启动 | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5090-128g/2026-11-27-sync/?env=rtx5090-128g&engine=strata,sync-strata "图表") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5090-128g/2026-11-27-sync/cases/plain/rtx5090-128g/README.zh.md "用例一览") [📁](published/plain/rtx5090-128g/2026-11-27-sync/ "证据") |

<details>
<summary>更早的 RUN（12 个）</summary>

| 测量完成 | 部门 | 引擎 | 环境 | RUN_ID | Tier | 用例（done / 全部） | 内容 | 查看 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-11-27 08:52 | 纯模型（无 harness） | Strata | GeForce RTX 5090 · 128 GB RAM | `2026-11-27-fix` | 4a, 5 | 14 / 14 | 重新测量 2026-11-25-main 未测得的 14 个用例（完成 14 个）：Gyro-S v2 的 256K 与 1M（已修正为在任何 context 下都以 jbench 的文件启动），以及 NVFP4 的 prefill chunk 1024、2048、4096（在调优预设不生效的状态下，以指定的 --prefill 启动） | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5090-128g/2026-11-27-fix/?env=rtx5090-128g "图表") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5090-128g/2026-11-27-fix/cases/plain/rtx5090-128g/README.zh.md "用例一览") [📁](published/plain/rtx5090-128g/2026-11-27-fix/ "证据") |
| 2026-11-27 03:55 | 纯模型（无 harness） | Strata | GeForce RTX 5090 · 128 GB RAM | `2026-11-25-main` | 0, 1, 2, 3, 4a, 4b, 4c, 4d, 5 | 1813 / 1835 | 在 Strata 0.2.21 上重新测量全部模型（27 个 build，含 Gyro-S v2 与 Inkling 2 Mini）的 Tier 0–5（1835 个用例完成 1813 个）。未测得：Gyro-S v2 的 256K 与 1M（jbench 未能启动）、NVFP4 的 prefill chunk（设置未传到引擎）、Hy4-Flash SQ-128 与 Inkling SQ-20 的 256K 长文（文档超出上下文窗口）。NVFP4 在 128K 的 103 个用例受 11 月 4 日调优预设影响，以 --prefill auto:32768 启动（在此显卡上与默认的 auto 上限相同，重测数值不变） | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5090-128g/2026-11-25-main/?env=rtx5090-128g "图表") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5090-128g/2026-11-25-main/cases/plain/rtx5090-128g/README.zh.md "用例一览") [📁](published/plain/rtx5090-128g/2026-11-25-main/ "证据") |
| 2026-11-22 15:52 | 纯模型（无 harness） | Strata | GeForce RTX 5090 · 128 GB RAM | `2026-11-22-hy4` | 1, 2, 3, 4a, 4b | 140 / 147 | 新增 Strata 0.2.18 支持的 Tencent Hy4-Flash（SQ-64、SQ-96、SQ-128）并测量（Tier 1–4b，147 个用例完成 140 个）。1M 启动时 GPU 显存不足，SQ-128 的 256K 文档按 Hy4 的分词器超出上下文窗口，均未测得 | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5090-128g/2026-11-22-hy4/?env=rtx5090-128g "图表") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5090-128g/2026-11-22-hy4/cases/plain/rtx5090-128g/README.zh.md "用例一览") [📁](published/plain/rtx5090-128g/2026-11-22-hy4/ "证据") |
| 2026-11-19 16:39 | 纯模型（无 harness） | Sync-Strata | GeForce RTX 5070 · Core Ultra 5 235 · 64 GB RAM · SATA SSD | `2026-11-19-sync-r10` | 1 | 54 / 54 | 在 Sync-Strata 0.1.1 上测量 Sync-XS、Sync-S 和 Sync-M 的 Tier 1，使用 R10（关闭 tail skip）、128K 上下文、k8v4 KV 和 MTP。54 个用例、162 个请求全部成功。 | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5070-cu5_235-64g-sata/2026-11-19-sync-r10/?env=rtx5070-cu5_235-64g-sata&engine=strata,sync-strata "图表") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5070-cu5_235-64g-sata/2026-11-19-sync-r10/cases/plain/rtx5070-cu5_235-64g-sata/README.zh.md "用例一览") [📁](published/plain/rtx5070-cu5_235-64g-sata/2026-11-19-sync-r10/ "证据") |
| 2026-11-10 06:23 | 纯模型（无 harness） | Strata | GeForce RTX 5070 · Core Ultra 5 235 · 64 GB RAM · SATA SSD | `2026-11-09-harbor-gyro-long-t5` | 0, 3, 4b, 4c, 5 | 224 / 236 | 测量了尚未测量的用例：全部 11 个模型的编程任务“帆船停靠港口”（Tier 0、3），gyro Gyro-S、Gyro-M 与 unsloth UD-Q2_K_XL 的长文（Tier 4b、4c），以及 Gyro-S、Gyro-M 的启动选项（Tier 5）。Tier 3 的 33 次帆船中 16 次画出了场景，1 次被截断。vram-reserve 40%・50% 的 12 个用例因 12 GB VRAM 放不下而无法启动 | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5070-cu5_235-64g-sata/2026-11-09-harbor-gyro-long-t5/?env=rtx5070-cu5_235-64g-sata "图表") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5070-cu5_235-64g-sata/2026-11-09-harbor-gyro-long-t5/cases/plain/rtx5070-cu5_235-64g-sata/README.zh.md "用例一览") [📁](published/plain/rtx5070-cu5_235-64g-sata/2026-11-09-harbor-gyro-long-t5/ "证据") |
| 2026-11-09 05:24 | 纯模型（无 harness） | Strata | GeForce RTX 5090 · 128 GB RAM | `2026-11-09-harbor` | 0, 3 | 21 / 21 | 将 plain 的编程任务换为“帆船停靠港口”（单个 HTML 的 3D 体素艺术，场景只给出标题）并测量（Tier 0、3，20 个模型）。思考 64K、输出 130,048 时，60 次中没有被截断的，36 次画出了场景 | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5090-128g/2026-11-09-harbor/?env=rtx5090-128g "图表") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5090-128g/2026-11-09-harbor/cases/plain/rtx5090-128g/README.zh.md "用例一览") [📁](published/plain/rtx5090-128g/2026-11-09-harbor/ "证据") |
| 2026-11-08 17:24 | 纯模型（无 harness） | Strata | GeForce RTX 5070 · Core Ultra 5 235 · 64 GB RAM · SATA SSD | `2026-11-08-gyro-coder` | 0, 1, 2, 3, 4a | 111 / 111 | 追加测量了 gyro Gyro-S 和 coder IQ1_M（Tier 0〜4a）。这两个模型在 2026-11-06-main 中因磁盘空间而被排除 | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5070-cu5_235-64g-sata/2026-11-08-gyro-coder/?env=rtx5070-cu5_235-64g-sata "图表") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5070-cu5_235-64g-sata/2026-11-08-gyro-coder/cases/plain/rtx5070-cu5_235-64g-sata/README.zh.md "用例一览") [📁](published/plain/rtx5070-cu5_235-64g-sata/2026-11-08-gyro-coder/ "证据") |
| 2026-11-08 08:46 | 纯模型（无 harness） | Strata | GeForce RTX 5070 · Core Ultra 5 235 · 64 GB RAM · SATA SSD | `2026-11-06-main` | 0, 1, 2, 3, 4a, 4b, 4c, 4d, 5 | 719 / 727 | 在 RTX 5070 · Core Ultra 5 235（PL1/PL2 65 W）· 64 GB · SATA SSD 上的首次完整测量（Tier 0〜5，9 个模型）。依赖从 SSD 重读权重的 Unsloth UD-IQ3_XXS、UD-Q3_K_XL 已排除 | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/?env=rtx5070-cu5_235-64g-sata "图表") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/cases/plain/rtx5070-cu5_235-64g-sata/README.zh.md "用例一览") [📁](published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/ "证据") |
| 2026-11-04 22:51 | 纯模型（无 harness） | Strata | GeForce RTX 5090 · 128 GB RAM | `2026-11-04-long` | 4b, 4c, 4d | 112 / 112 | Tier 4b・4c・4d（32K〜1M 的长文阅读与 YaRN 检查）。2026-11-03-main 因长文 fixture 尚未制作而省略，之后用青空文库与 Project Gutenberg 的日英 10 部作品制作长文补测 | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5090-128g/2026-11-04-long/?env=rtx5090-128g "图表") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5090-128g/2026-11-04-long/cases/plain/rtx5090-128g/README.zh.md "用例一览") [📁](published/plain/rtx5090-128g/2026-11-04-long/ "证据") |
| 2026-11-04 18:20 | 纯模型（无 harness） | Strata | GeForce RTX 5090 · 128 GB RAM | `2026-11-04-q8-t3` | 3 | 9 / 9 | unsloth Q8_0 的 Tier 3（有无 thinking 与编程）。最初的计划把 Q8_0 排除在 Tier 3 之外，因此加入计划后补测 | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5090-128g/2026-11-04-q8-t3/?env=rtx5090-128g "图表") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5090-128g/2026-11-04-q8-t3/cases/plain/rtx5090-128g/README.zh.md "用例一览") [📁](published/plain/rtx5090-128g/2026-11-04-q8-t3/ "证据") |
| 2026-11-04 15:25 | 纯模型（无 harness） | Strata | GeForce RTX 5090 · 128 GB RAM | `2026-11-04-iq3s-mtp` | 0, 1, 2, 3, 4a, 5 | 159 / 159 | qwen IQ3_S 的重测（2026-11-03-main 中 MTP 的 draft layer 未加载）。包括 DFlash2 用例在内重跑了相同的 Tier | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5090-128g/2026-11-04-iq3s-mtp/?env=rtx5090-128g "图表") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5090-128g/2026-11-04-iq3s-mtp/cases/plain/rtx5090-128g/README.zh.md "用例一览") [📁](published/plain/rtx5090-128g/2026-11-04-iq3s-mtp/ "证据") |
| 2026-11-04 10:41 | 纯模型（无 harness） | Strata | GeForce RTX 5090 · 128 GB RAM | `2026-11-03-main` | 0, 1, 2, 3, 4a, 5 | 1231 / 1231 | 第一次完整测量（Tier 0・1・2・4a・3・5，18 个模型）。其中 qwen IQ3_S 未启用 MTP，页面使用重测的 2026-11-04-iq3s-mtp | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5090-128g/2026-11-03-main/?env=rtx5090-128g "图表") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5090-128g/2026-11-03-main/cases/plain/rtx5090-128g/README.zh.md "用例一览") [📁](published/plain/rtx5090-128g/2026-11-03-main/ "证据") |

</details>
<!-- published-runs:end -->

## 测量了什么

一次测量针对**一个引擎**（官方 Strata、衍生引擎，或已启动的引擎）、**一个环境**（该电脑的硬件），测量所选的**模型**与**项目**。

### 项目

| 项目 | 回答的问题 | 发送的内容 |
| --- | --- | --- |
| **生成速度**<br>`speed-decode` | 生成文本有多快？ | 5 种简短指令（日语说明文、英语说明文、JSON、Python 代码、照抄给定文本），输出最多 512 token，temperature 0 / 0.7 / 1.0，thinking off，各 3 次。支持 DFlash2 的模型再用 DFlash2 测一次 |
| **读取速度**<br>`speed-prefill` | 读取长输入有多快，到第一个字符要等多久？ | 把固定的记录列表精确截到 4K / 32K / 128,000 token（与 Strata 的 standard-v1 相同的构造方式），输出最多 128 token，temperature 0.7，thinking off，各 3 次 |
| **Strata 官方标准基准**<br>`official-standard` | 官方标准基准（standard-v1）的结果如何？ | 原样运行 strata bench run --suite standard-v1 共 3 次（thinking xhigh，temperature 1.0，9 个性能请求 + 12 道 sanity 题）。其 fixture 按 Qwen3.8 的 tokenizer 定长，其他基础模型的 token 数不一致 |
| **思考后作答**<br>`think-qa` | 开启思考后，作答时间与正确率如何变化？ | 4 道可自动判定答案的题（数学、代码（运行测试判定）、日语推理、英语推理），分别在 thinking off 与 on（xhigh）下，输出最多 16,384 token，temperature 1.0，各 3 次。没有 thinking 的模型只测 off |
| **一次请求生成页面**<br>`code-oneshot` | 一次请求能写出可运行的页面吗？ | 用英文请求把“停靠港口的帆船”场景做成单个 HTML 文件的 3D 体素艺术。思考 64K，输出用满 128K 窗口，temperature 1.0，3 次。页面在 headless Chrome 中运行 10 秒，记录报错、是否卡死、是否有绘制 |
| **预留上下文的代价**<br>`context-reserve` | 仅仅预留更大的上下文就会变慢吗？ | 分别以 128K / 256K / 1M 上下文启动，相同的 4K 输入 + 512 输出各 3 次。能否以 1M 启动也在此体现 |
| **长文阅读**<br>`long-read` | 真正读入长文档时，速度与正确率如何？（至 1M token） | 由青空文库与 Project Gutenberg 的 10 部日英作品拼成的文档，长度 32K / 128K / 256K（训练范围）与 512K / 1M（扩展范围）。对埋在 10% / 50% / 90% 位置的事实各问一题，最后一题需要综合多处。各 3 次。仅代表模型 |
| **YaRN 的影响**<br>`yarn-check` | 超出训练长度的设置（YaRN）会改变相同输入的结果吗？ | 约 300K 输入在 384K 容量下（有 / 无 YaRN），约 200K 输入在 256K 与 1M 容量下。仅基准模型 |
| **启动选项的效果**<br>`launch-options` | 哪些启动选项有效？ | 每次只改基准启动的一项（drafter、draft 深度、KV 格式、prefill chunk、VRAM 分配、vision、CPU 分配、PLE 表位置、并行、自动 tune），2 种生成与 2 种读取用例各 3 次。仅代表模型 |
| **测量自检**<br>`selfcheck` | 测量本身是否正确，重新启动之间波动多大？ | 在基准模型上分 3 次启动测量“生成速度”“读取速度”；按作者公开的条件测 Gyro-S 并与公开数值比较；跑一次编程任务以确认成果提取。每个环境一次 |
| **交给智能体**<br>`agent-oneshot` | 一次性交给智能体 harness，需要多久、能做出什么？ | 把“做一个类似 Minecraft 的 3D 沙盒游戏”（日语）不加格式说明、一次性交给 harness。思考 32K，输出用满窗口，每次最多 3,600 秒，3 次。记录代理把 sampling、thinking、seed 与输出上限对所有 harness 统一 |

项目按“预设”打包：`quick`（只测两个头条速度数字，数分钟）、`standard`（生成、读取、思考后作答、生成页面）、`full`（全部）。
项目与用例的对应以及各用例的条件见上表的“用例一览”（Tier 是项目的旧称，用例一览与图表仍同时标注）。定义在 [catalog/tasks.json](catalog/tasks.json) 与 [scripts/case_plan.py](scripts/case_plan.py)。

### 头条数字

最先看的数字都取自**一个固定条件**。多种用例的汇总值（平均、中位数的中位数）不作为头条。

| 名称 | 定义 |
| --- | --- |
| **JB-decode** 生成速度 | 生成英语说明文时的 decode tok/s：temperature 0.7，thinking off，上下文 128K，drafter 为引擎自己的选择（Strata 的 Auto：支持 DFlash2 的模型用 DFlash2，其余用 MTP 或内置 drafter），3 次的中位数 |
| **JB-ttft-32k** 读入 32K 后的首字符时间 | 发送 32K token 输入到收到第一个字符的秒数：thinking off，上下文 128K，3 次的中位数 |
| **JB-answer** 思考后作答 | 在 thinking on 下 4 题的正确数（0〜4，3 次中至少 2 次正确算正确）与完成秒数的中位数。没有 thinking 的模型取 off 的值 |
| **JB-page** 一次生成的页面 | 3 次中无报错并成功绘制的页面数（0〜3） |
| **JB-agent** 交给智能体的结果 | 3 次中成功绘制的游戏数（0〜3）与完成秒数的中位数 |

按文本种类、temperature、drafter 等的细分都在图表页面。各指标的定义在 [catalog/metrics.json](catalog/metrics.json) 中各占一行。

### 引擎与模型

| 引擎 | 测量方式 |
| --- | --- |
| **Strata** (`strata`) | 官方 Strata。用 `strata launch` 启动，并核对所要求的设置是否到达引擎的命令行。 |
| **Sync-Strata** (`sync-strata`) | Strata 的分支，用自己的量化 Sync-XS / S / M 运行 Qwen3.8-Flash-Next（格式与上游不兼容）。用 `sync up --api-only` 启动，每次 run 使用独立的设置目录。 |
| **OpenAI-compatible endpoint (attach only)** (`endpoint`) | 只连接到已启动的引擎的 URL。jbench 不启动也不停止它，因此无法核对启动方式（结果标注“仅连接”）。用于先试用没有适配器的衍生引擎。 |

以质量换速度的设置（如 Sync-Strata 的 tail skip）默认关闭后测量（`exact`）。按引擎默认设置测得的结果（`default`）单独对待，不混合。

模型按基础模型放在 [catalog/models/](catalog/models/)：Qwen3.8-Flash-Next（28）、Tencent Hy4-Flash（3）、Thinking Machines Inkling 2 Mini（3）。tokenizer 相同的模型输入 token 数相同，tok/s 可以直接比较；tokenizer 不同的模型之间仅供参考。

### 同一把尺子

- 测量条件写成一段文本“配方”，其 id（引擎、设置类别、驱动方式、项目及其版本的 hash）随结果保存。
- 每个用例也带有自身条件的 hash（提示词的 SHA-256、上下文、启动选项、thinking、temperature、输出上限、seed）。跨环境并排比较的只有 hash 相同的用例。
- 无法确认所要求的设置已到达引擎的用例记为失败，不计为速度数字。

### 测量方法

- 不使用 Strata 的桌面应用。用 CLI 的 `strata launch --no-tui` 在专用端口启动引擎，由 [scripts/bench_runner.py](scripts/bench_runner.py)
  直接调用其 OpenAI 兼容的 HTTP API（`POST /v1/chat/completions`，流式）。不经过智能体 harness，也不附加 tool 定义（纯模型部门）；
  聊天模板与分词由 Strata 的服务器完成。只有 Tier 2 对同一引擎运行自带的 `strata bench run --suite standard-v1`。
- 除非用例另有指定，drafter 固定为 MTP（`--drafting mtp --mtp on`）。thinking 与采样设置在每次请求中明确指定。
- 输入是 [prompts/](prompts/) 中的固定提示（`MANIFEST.json` 中有 SHA-256）。为避免使用之前回答的缓存，每个请求开头都加入唯一 ID。
- Tier 4b〜4d 的长文由 10 部已过版权期的日英作品交替排列而成（青空文库：夏目漱石、岛崎藤村、有岛武郎、太宰治、宫泽贤治；
  Project Gutenberg：Melville、Austen、Dickens、Shelley、Doyle；来源与底本见 [prompts/long-sources.json](prompts/long-sources.json)）。
  在文档的 10 / 50 / 90% 处放置虚构的事实并提问。同一文档的后续问题从 prefix cache 读取文档部分。
- 测量期间不同时运行其他繁重处理（下载、转换、其他推理引擎）。

### 测量环境

按硬件配置（GPU 与 RAM 的组合，即“环境”）分开。不同环境的结果不会混在一起，用图表页面上方的按钮切换。
两个以上环境有结果时，会出现以相同模型・相同条件并排的“环境比较”。
各环境的配置（GPU、CPU、内存、驱动、Strata 版本等）见图表页面与用例一览的开头，定义在 [envs/](envs/)。

## 数据位置

测量记录在 `published/<部门>/<环境>/<RUN_ID>/`（目前只有 `published/plain/…`）。

| 内容 | 位置 |
| --- | --- |
| 各用例的结果 | `cases/<case id>/summary.json`（汇总）、`requests.jsonl`（所发请求）、`responses/`（回答正文）、`artifact/`（编程任务的产物） |
| 每次启动的记录 | `sessions/<session>/start-N/`（`strata launch` 的输出、引擎日志、/settings・/config・/props、telemetry.csv） |
| standard-v1 的输出 | `standard/` |
| 温度・功耗的变化 | `stats/thermal.csv`（每 5 秒） |
| 测量的模型版本 | `models.json`（各模型的 Hugging Face 仓库与提交，各文件的大小与 SHA-256，以及测量开始时本地文件是否为该 SHA-256）。同名模型在发布者更新后内容会变，由此可知测量的是哪个版本。用例一览的模型一览和图表页面中各 RUN_ID 的行也链接到它 |
| 队列与 runner 的日志 | `queue.log`、`runner.log` |
| 该 RUN 的说明 | `NOTE.md`（上表的“内容”） |
| 记录之间的核对 | `verify.json`（引擎 timings 与客户端计时的差、启动设置是否进入引擎） |
| tune 的结果 | `sessions/*-tune-*/start-1/tune-presets.json`；各模型的汇总见 [configs/tuned/](configs/tuned/) |

流的原始数据（SSE 与思考全文）以及包含 PC 上全部进程的机器快照不公开。公开的日志中，主文件夹写作 `~`，主机名写作 `<host>`。

### 只留在本机的内容

运行仓库中的脚本时，会在仓库内生成以下文件夹。它们都不在 Git 中（[.gitignore](.gitignore)），也不会被发送到任何地方
（访问网络的只有模型的下载）。

| 文件夹 | 生成者 | 内容 |
| --- | --- | --- |
| `results/` | `scripts/bench_runner.py` 等 | 测量中的结果，移到 `published/` 之前放在这里 |
| `results/…/<RUN_ID>/raw/` | `scripts/bench_runner.py` | 流的原始数据（SSE 与思考全文），不移到 `published/` |
| `results/…/<RUN_ID>/stats/snapshots.jsonl.gz`、`last.json` | `scripts/stats_watch.py` | **测量期间整台 PC 的快照**。在会话开始、启动、用例结束、失败、Tier 切换时以及每 5 分钟，记录所有运行中的进程（PID、用户名、完整命令行、CPU・内存・磁盘 IO）、使用 GPU 的进程，以及 CPU・内存・PSI・温度。用于事后确认并行的处理是否干扰了测量。由于会留下其他程序的命令行（包括作为参数写入的路径和值），不移到 `published/` |
| `preview/` | `scripts/build_cases.py`、`scripts/build_results.py` | 同时读取 `results/` 生成的检查用图表与用例一览 |
| `run-status/` | `scripts/bench.py`、`scripts/healthcheck.py`、`scripts/preflight.py` | 无人值守运行的状态（`STATUS.md`、`ALERTS.log`、`current-run.json`、`preflight.json`） |
| `downloads/` | `scripts/download_models.py`、`scripts/overnight.py` | 模型下载的状态与日志（`manifest.json` 含 SHA-256） |
| `work/` | `scripts/overnight.py`（NVFP4-QAD 转换） | NVFP4-QAD 转换用的工作文件夹。长文语料的原始数据（`work/corpus/raw/`，手动获取）也放在这里，由 `scripts/long_corpus.py` 读取 |

不想记录快照时，请在开始前于 `bench.json` 写入 `"stats": false`。不再需要时，可以删除 `results/` 中的内容。
仓库顶层的 `bench.json`（测量设置）也不在 Git 中。

在仓库之外，模型权重存放在 `~/.local/share/strata/Strata-data/models`，Strata 的启动配置
（`launch-<model>-<context>`）和 Tier 5 tune 的预设写入 Strata 的设置。测量期间会运行与终端分离的
监视进程（`scripts/supervise.py`）及其子进程，不创建 systemd 单元。

## 复现

测量耗时很长，因此由脱离终端的监督进程无人值守地运行（卡住的用例的重启和状态记录也由它负责）。

**交给智能体**（推荐）：克隆本仓库，让 Claude Code 等智能体“用 strata-jbench 测量”。
仓库附带的 [strata-jbench 技能](.claude/skills/strata-jbench/SKILL.md)会引导完成：确认环境 → 在配置器中选择 → 确认计划与缺少的东西 → 开始 → 监视 → 检查结果。
缺少的引擎、harness、模型，会先询问“可否下载到仓库内的 `tools/`（不纳入 Git），或者电脑上已有的话在哪里”，然后再准备。

**手动运行**：

```bash
python3 -I scripts/envs.py list                  # 与当前硬件匹配的环境
python3 -I scripts/build_configurator.py         # 生成 preview/configurator.html（在浏览器中打开并选择）
python3 -I scripts/bench.py recipe --apply FILE  # 把复制的配方写入 bench.json
python3 -I scripts/bench.py plan                 # 所选范围的用例数与预计时间
python3 -I scripts/acquire.py check              # 缺少的东西（模型、引擎、harness）
python3 -I scripts/bench.py start                # 检查后开始（监督进程脱离终端运行）
python3 -I scripts/bench.py status               # 状态
python3 -I scripts/bench.py stop                 # 停止（用相同 run_id 再次 start 即可续跑）
```

测量官方 Strata 需要先安装 Strata（桌面应用）并通过它安装过一次模型，并把 Strata 的源码放在 `~/Strata`（要获取的文件及其 SHA-256 由源码的 `setup.py` 决定）。
完整步骤见 [AGENTS.md](AGENTS.md) 与技能的 [references/](.claude/skills/strata-jbench/references/)（英文），环境定义的写法见 [envs/README.md](envs/README.md)。
想提供自己测得的结果，请把确定的 RUN（`published/<部门>/<环境>/<RUN_ID>/`）以 pull request 发送。

## 许可证

- **代码**（脚本、页面模板、页面本身的代码）：[MIT License](LICENSE)
- **测量数据**（`published/`、`snapshots/`、`cases/`、`configs/tuned/`，以及页面上的数值与图表）：[CC BY 4.0](LICENSE-DATA.md)。
  引用时请注明“strata-jbench”并附上本仓库链接，以及环境与 RUN_ID（例如 `rtx5090-128g / 2026-11-03-main`）。
- **长文素材**（`prompts/long-corpus.txt` 中 10 部作品的正文）：公有领域。来源与底本见 [prompts/long-sources.json](prompts/long-sources.json)。
- 模型、模型名称与 Strata 遵循各自作者的许可证。

## 参考与致谢

- **[Strata](https://github.com/Niko1221/Strata)**（Niko1221 and the Strata contributors，MIT License）：本次测量所用的本地 LLM 推理引擎。Tier 2 的 standard-v1 也是 Strata 自带的基准。
- **[Sync-Strata](https://github.com/hiruhiru2005/sync-strata)**（hiruhiru2005）：Strata 的分支及其量化 Sync-XS / S / M，在此作为衍生引擎测量。
- **[青空文库](https://www.aozora.gr.jp/)**：长文中的 5 部日语作品（夏目漱石《我是猫》、岛崎藤村《破戒》、有岛武郎《某个女人》、太宰治《人间失格》、宫泽贤治《银河铁道之夜》）。
  感谢录入与校对的志愿者。各作品的底本・录入・校对信息保留在 `prompts/long-sources.json`。
- **[Project Gutenberg](https://www.gutenberg.org/)**：长文中的 5 部英语作品（Melville《白鲸》、Austen《傲慢与偏见》、Dickens《双城记》、Shelley《弗兰肯斯坦》、Doyle《福尔摩斯探案集》）。
  按照 Project Gutenberg 的条款，只使用去掉页眉、许可证与商标表述后的正文。
- **模型**：Qwen3.8-Flash-Next（Qwen），以及其量化版与派生版的作者们。

| 仓库 | 在本基准中的名称 |
| --- | --- |
| [ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF) | qwen Q2_0, IQ2_XS, IQ3_XXS, IQ3_S |
| [ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-Coder-GGUF](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-Coder-GGUF) | coder IQ1_M |
| [agentionai/Qwen3.8-Flash-Next-Gyro-GGUF](https://huggingface.co/agentionai/Qwen3.8-Flash-Next-Gyro-GGUF) | gyro Gyro-S, Gyro-M |
| [unsloth/Qwen3.8-Flash-Next-GGUF](https://huggingface.co/unsloth/Qwen3.8-Flash-Next-GGUF) | unsloth UD-IQ4_XS, UD-Q4_K_XL, UD-Q5_K_XL, UD-Q6_K_XL, Q8_0 |
| [ukisai/Swift-1.5-Qwen3.8-Flash-Next-GSQ-RCO-GGUF](https://huggingface.co/ukisai/Swift-1.5-Qwen3.8-Flash-Next-GSQ-RCO-GGUF) | swift IQ2_XS, IQ3_XXS, IQ3_S |
| [Maximilian228/Qwen3.8-Flash-Next-NVFP4-GPTQ-Strata](https://huggingface.co/Maximilian228/Qwen3.8-Flash-Next-NVFP4-GPTQ-Strata) | nvfp4 NVFP4 |
| [Maximilian228/Qwen3.8-Flash-Next-NVIDIA-NVFP4-Strata](https://huggingface.co/Maximilian228/Qwen3.8-Flash-Next-NVIDIA-NVFP4-Strata) | nvfp4 NVFP4-NVIDIA |
| [nvidia/Qwen3.8-Flash-Next-FP4-Local](https://huggingface.co/nvidia/Qwen3.8-Flash-Next-FP4-Local) | nvfp4 NVFP4-QAD（面向 FP4 的再训练；在测量用的 PC 上用 Strata 自带的工具转换为 Strata 的格式，由 `scripts/overnight.py` 执行） |
