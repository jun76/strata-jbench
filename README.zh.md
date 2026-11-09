<p align="center"><picture>
  <source media="(prefers-color-scheme: dark)" srcset="media/strata-jbench.png">
  <img src="media/strata-jbench-light.png" alt="strata-jbench" width="560">
</picture></p>

[日本語](README.md) | [English](README.en.md) | **中文**

在本地 LLM 推理引擎 Strata 上，以相同条件测量 Qwen3.8-Flash-Next 的 18 个量化版与派生版模型的结果。
计划、测量脚本和原始记录也一并放在这里，可以按同样的步骤复现。

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
| 测量完成 | 部门 | 环境 | RUN_ID | Tier | 用例（done / 全部） | 内容 | 查看 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-11-10 06:23 | 纯模型（无 harness） | GeForce RTX 5070 · Core Ultra 5 235 · 64 GB RAM · SATA SSD | `2026-11-09-harbor-gyro-long-t5` | 0, 3, 4b, 4c, 5 | 224 / 236 | 测量了尚未测量的用例：全部 11 个模型的编程任务“帆船停靠港口”（Tier 0、3），gyro Gyro-S、Gyro-M 与 unsloth UD-Q2_K_XL 的长文（Tier 4b、4c），以及 Gyro-S、Gyro-M 的启动选项（Tier 5）。Tier 3 的 33 次帆船中 16 次画出了场景，1 次被截断。vram-reserve 40%・50% 的 12 个用例因 12 GB VRAM 放不下而无法启动 | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5070-cu5_235-64g-sata/2026-11-09-harbor-gyro-long-t5/?env=rtx5070-cu5_235-64g-sata "图表") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5070-cu5_235-64g-sata/2026-11-09-harbor-gyro-long-t5/cases/plain/rtx5070-cu5_235-64g-sata/README.zh.md "用例一览") [📁](published/plain/rtx5070-cu5_235-64g-sata/2026-11-09-harbor-gyro-long-t5/ "证据") |
| 2026-11-09 05:24 | 纯模型（无 harness） | GeForce RTX 5090 · 128 GB RAM | `2026-11-09-harbor` | 0, 3 | 21 / 21 | 将 plain 的编程任务换为“帆船停靠港口”（单个 HTML 的 3D 体素艺术，场景只给出标题）并测量（Tier 0、3，20 个模型）。思考 64K、输出 130,048 时，60 次中没有被截断的，36 次画出了场景 | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5090-128g/2026-11-09-harbor/?env=rtx5090-128g "图表") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5090-128g/2026-11-09-harbor/cases/plain/rtx5090-128g/README.zh.md "用例一览") [📁](published/plain/rtx5090-128g/2026-11-09-harbor/ "证据") |
| 2026-11-08 17:24 | 纯模型（无 harness） | GeForce RTX 5070 · Core Ultra 5 235 · 64 GB RAM · SATA SSD | `2026-11-08-gyro-coder` | 0, 1, 2, 3, 4a | 111 / 111 | 追加测量了 gyro Gyro-S 和 coder IQ1_M（Tier 0〜4a）。这两个模型在 2026-11-06-main 中因磁盘空间而被排除 | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5070-cu5_235-64g-sata/2026-11-08-gyro-coder/?env=rtx5070-cu5_235-64g-sata "图表") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5070-cu5_235-64g-sata/2026-11-08-gyro-coder/cases/plain/rtx5070-cu5_235-64g-sata/README.zh.md "用例一览") [📁](published/plain/rtx5070-cu5_235-64g-sata/2026-11-08-gyro-coder/ "证据") |

<details>
<summary>更早的 RUN（5 个）</summary>

| 测量完成 | 部门 | 环境 | RUN_ID | Tier | 用例（done / 全部） | 内容 | 查看 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-11-08 08:46 | 纯模型（无 harness） | GeForce RTX 5070 · Core Ultra 5 235 · 64 GB RAM · SATA SSD | `2026-11-06-main` | 0, 1, 2, 3, 4a, 4b, 4c, 4d, 5 | 719 / 727 | 在 RTX 5070 · Core Ultra 5 235（PL1/PL2 65 W）· 64 GB · SATA SSD 上的首次完整测量（Tier 0〜5，9 个模型）。依赖从 SSD 重读权重的 Unsloth UD-IQ3_XXS、UD-Q3_K_XL 已排除 | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/?env=rtx5070-cu5_235-64g-sata "图表") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/cases/plain/rtx5070-cu5_235-64g-sata/README.zh.md "用例一览") [📁](published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/ "证据") |
| 2026-11-04 22:51 | 纯模型（无 harness） | GeForce RTX 5090 · 128 GB RAM | `2026-11-04-long` | 4b, 4c, 4d | 112 / 112 | Tier 4b・4c・4d（32K〜1M 的长文阅读与 YaRN 检查）。2026-11-03-main 因长文 fixture 尚未制作而省略，之后用青空文库与 Project Gutenberg 的日英 10 部作品制作长文补测 | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5090-128g/2026-11-04-long/?env=rtx5090-128g "图表") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5090-128g/2026-11-04-long/cases/plain/rtx5090-128g/README.zh.md "用例一览") [📁](published/plain/rtx5090-128g/2026-11-04-long/ "证据") |
| 2026-11-04 18:20 | 纯模型（无 harness） | GeForce RTX 5090 · 128 GB RAM | `2026-11-04-q8-t3` | 3 | 9 / 9 | unsloth Q8_0 的 Tier 3（有无 thinking 与编程）。最初的计划把 Q8_0 排除在 Tier 3 之外，因此加入计划后补测 | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5090-128g/2026-11-04-q8-t3/?env=rtx5090-128g "图表") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5090-128g/2026-11-04-q8-t3/cases/plain/rtx5090-128g/README.zh.md "用例一览") [📁](published/plain/rtx5090-128g/2026-11-04-q8-t3/ "证据") |
| 2026-11-04 15:25 | 纯模型（无 harness） | GeForce RTX 5090 · 128 GB RAM | `2026-11-04-iq3s-mtp` | 0, 1, 2, 3, 4a, 5 | 159 / 159 | qwen IQ3_S 的重测（2026-11-03-main 中 MTP 的 draft layer 未加载）。包括 DFlash2 用例在内重跑了相同的 Tier | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5090-128g/2026-11-04-iq3s-mtp/?env=rtx5090-128g "图表") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5090-128g/2026-11-04-iq3s-mtp/cases/plain/rtx5090-128g/README.zh.md "用例一览") [📁](published/plain/rtx5090-128g/2026-11-04-iq3s-mtp/ "证据") |
| 2026-11-04 10:41 | 纯模型（无 harness） | GeForce RTX 5090 · 128 GB RAM | `2026-11-03-main` | 0, 1, 2, 3, 4a, 5 | 1231 / 1231 | 第一次完整测量（Tier 0・1・2・4a・3・5，18 个模型）。其中 qwen IQ3_S 未启用 MTP，页面使用重测的 2026-11-04-iq3s-mtp | [📈](https://jun76.github.io/strata-jbench/snapshots/plain/rtx5090-128g/2026-11-03-main/?env=rtx5090-128g "图表") [📋](https://github.com/jun76/strata-jbench/blob/run/plain/rtx5090-128g/2026-11-03-main/cases/plain/rtx5090-128g/README.zh.md "用例一览") [📁](published/plain/rtx5090-128g/2026-11-03-main/ "证据") |

</details>
<!-- published-runs:end -->

## 测量了什么

纯模型部门的测量分为若干层级（Tier）。用例定义在 [scripts/build_cases.py](scripts/build_cases.py)，各用例的条件可在上表的“用例一览”中查看。

| Tier | 看什么 | 对象 |
| --- | --- | --- |
| 0 | 测量本身是否正确、波动有多大 | 部分模型 |
| 1 | 各模型的基本速度（prefill・decode，按文章种类、temperature、drafter） | 全部模型 |
| 2 | Strata 自带基准 standard-v1 的速度与 sanity 正确率 | 全部模型 |
| 3 | 有无 thinking 对到回答的时间、正确率和编程结果的影响 | 全部模型 |
| 4 | 预留上下文长度的代价（4a）与实际长文处理（4b〜4d，至 1M token） | 4a 为全部模型，4b〜4d 为代表模型 |
| 5 | 逐个改变启动选项时的变化（含自动 tune） | 3 个代表模型 |

各个 RUN 包含哪些 Tier，见上表的“Tier”列。

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

测量耗时很长，因此在与终端分离的监视进程下无人值守运行（失败或卡住的运行器的重启与状态记录也由它负责）。步骤（准备环境、preflight、开始、监视、异常恢复、确定结果）见
[AGENTS.md](AGENTS.md)（英语），环境定义的写法见 [envs/README.md](envs/README.md)。

前提是已安装 Strata（桌面应用）并安装过一次模型，且 Strata 的源码位于 `~/Strata`（下载哪些文件及其 SHA-256 由源码的
`setup.py` 决定）。下载用和 NVFP4-QAD 转换用的 Python 环境由 `scripts/setup_acquire.py` 创建，`scripts/bench.py start` 会自动调用它。
测量设置（RUN_ID、部门、要运行的 Tier・模型・用例等）写在 `bench.json` 中，`scripts/bench.py config` 可列出全部项目及默认值。

```bash
python3 -I scripts/envs.py list          # 与当前硬件匹配的环境
python3 -I scripts/bench.py config        # 全部设置（bench.json 中的值与默认值）
python3 -I scripts/bench.py plan          # 所选范围的用例数与预估时间
python3 -I scripts/bench.py start         # 检查后开始（监视进程与终端分离运行）
python3 -I scripts/bench.py status        # 运行状况
python3 -I scripts/bench.py stop          # 停止（以同一 run_id 再次 start 会接着运行）
```

## 许可证

- **代码**（脚本、页面模板、页面本身的代码）：[MIT License](LICENSE)
- **测量数据**（`published/`、`snapshots/`、`cases/`、`configs/tuned/`，以及页面上的数值与图表）：[CC BY 4.0](LICENSE-DATA.md)。
  引用时请注明“strata-jbench”并附上本仓库链接，以及环境与 RUN_ID（例如 `rtx5090-128g / 2026-11-03-main`）。
- **长文素材**（`prompts/long-corpus.txt` 中 10 部作品的正文）：公有领域。来源与底本见 [prompts/long-sources.json](prompts/long-sources.json)。
- 模型、模型名称与 Strata 遵循各自作者的许可证。

## 参考与致谢

- **[Strata](https://github.com/Niko1221/Strata)**（Niko1221 and the Strata contributors，MIT License）：本次测量所用的本地 LLM 推理引擎。Tier 2 的 standard-v1 也是 Strata 自带的基准。
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
