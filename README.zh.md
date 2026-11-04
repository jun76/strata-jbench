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

| 页面 | 内容 |
| --- | --- |
| [RESULTS.html](RESULTS.html) | 用图表汇总的结果：各模型速度、输入长度与等待时间、standard-v1、有无 thinking、预留上下文长度的代价、长文阅读（至 1M token）、启动选项、测量时的温度・功耗・内存、各模型一览 |
| [CASES.html](CASES.html) | 各环境的全部用例：每个用例的条件、结果，以及所发请求和所得回答的链接 |
| [published/summary.csv](published/summary.csv) | 全部用例的数值（`division` 列区分部门，`env` 列区分环境） |

页面是静态 HTML。GitHub 的文件视图只显示源码，请 clone 仓库后在浏览器中打开（如已配置 GitHub Pages，也可从那里查看）。
页面右上角可切换日本語・English・中文，以及浅色・深色。

## 已确定的结果

每当有结果确定，本表就会增加一行（`scripts/publish.py` 根据 `published/` 重写）。
同一环境中同一用例出现在多个 RUN_ID 时，页面使用名称排在最后的 RUN_ID 的结果。

<!-- published-runs:start (scripts/publish.py writes this list) -->
| 测量完成 | 部门 | 环境 | RUN_ID | Tier | 用例（done / 全部） | 内容 | 查看 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-11-04 22:51 | 纯模型（无 harness） | GeForce RTX 5090 · 128 GB RAM | [`2026-11-04-long`](published/plain/rtx5090-128g/2026-11-04-long/) | 4b, 4c, 4d | 112 / 112 | Tier 4b・4c・4d（32K〜1M 的长文阅读与 YaRN 检查）。2026-11-03-main 因长文 fixture 尚未制作而省略，之后用青空文库与 Project Gutenberg 的日英 10 部作品制作长文补测 | [图表](RESULTS.html?env=rtx5090-128g) · [用例一览](cases/plain/rtx5090-128g.html) |
| 2026-11-04 18:20 | 纯模型（无 harness） | GeForce RTX 5090 · 128 GB RAM | [`2026-11-04-q8-t3`](published/plain/rtx5090-128g/2026-11-04-q8-t3/) | 3 | 9 / 9 | unsloth Q8_0 的 Tier 3（有无 thinking 与游戏制作）。最初的计划把 Q8_0 排除在 Tier 3 之外，因此加入计划后补测 | [图表](RESULTS.html?env=rtx5090-128g) · [用例一览](cases/plain/rtx5090-128g.html) |
| 2026-11-04 15:25 | 纯模型（无 harness） | GeForce RTX 5090 · 128 GB RAM | [`2026-11-04-iq3s-mtp`](published/plain/rtx5090-128g/2026-11-04-iq3s-mtp/) | 0, 1, 2, 3, 4a, 5 | 159 / 159 | qwen IQ3_S 的重测（2026-11-03-main 中 MTP 的 draft layer 未加载）。包括 DFlash2 用例在内重跑了相同的 Tier | [图表](RESULTS.html?env=rtx5090-128g) · [用例一览](cases/plain/rtx5090-128g.html) |
| 2026-11-04 10:41 | 纯模型（无 harness） | GeForce RTX 5090 · 128 GB RAM | [`2026-11-03-main`](published/plain/rtx5090-128g/2026-11-03-main/) | 0, 1, 2, 3, 4a, 5 | 1231 / 1231 | 第一次完整测量（Tier 0・1・2・4a・3・5，18 个模型）。其中 qwen IQ3_S 未启用 MTP，页面使用重测的 2026-11-04-iq3s-mtp | [图表](RESULTS.html?env=rtx5090-128g) · [用例一览](cases/plain/rtx5090-128g.html) |
<!-- published-runs:end -->

## 测量了什么

纯模型部门的测量分为若干层级（Tier）。用例定义在 [scripts/build_cases.py](scripts/build_cases.py)，各用例的条件可在 CASES.html 查看。

| Tier | 看什么 | 对象 |
| --- | --- | --- |
| 0 | 测量本身是否正确、波动有多大 | 部分模型 |
| 1 | 各模型的基本速度（prefill・decode，按文章种类、temperature、drafter） | 全部模型 |
| 2 | Strata 自带基准 standard-v1 的速度与 sanity 正确率 | 全部模型 |
| 3 | 有无 thinking 对到回答的时间、正确率和游戏制作的影响 | 全部模型 |
| 4 | 预留上下文长度的代价（4a）与实际长文处理（4b〜4d，至 1M token） | 4a 为全部模型，4b〜4d 为代表模型 |
| 5 | 逐个改变启动选项时的变化（含自动 tune） | 3 个代表模型 |

各个已确定的结果包含哪些 Tier，见上表的“Tier”列。

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

按硬件配置（GPU 与 RAM 的组合，即“环境”）分开。不同环境的结果不会混在一起，用 RESULTS.html 上方的按钮切换。
两个以上环境有结果时，会出现以相同模型・相同条件并排的“环境比较”。
各环境的配置（GPU、CPU、内存、驱动、Strata 版本等）见 RESULTS.html 与 CASES.html 开头，定义在 [envs/](envs/)。

## 数据位置

已确定的结果在 `published/<部门>/<环境>/<RUN_ID>/`（目前只有 `published/plain/…`）。

| 内容 | 位置 |
| --- | --- |
| 各用例的结果 | `cases/<case id>/summary.json`（汇总）、`requests.jsonl`（所发请求）、`responses/`（回答正文）、`artifact/`（游戏制作等的产物） |
| 每次启动的记录 | `sessions/<session>/start-N/`（`strata launch` 的输出、引擎日志、/settings・/config・/props、telemetry.csv） |
| standard-v1 的输出 | `standard/` |
| 温度・功耗的变化 | `stats/thermal.csv`（每 5 秒） |
| 机器配置 | `machine.json` |
| 队列与 runner 的日志 | `queue.log`、`runner.log` |
| 该 RUN 的说明 | `NOTE.md`（上表的“内容”） |
| 记录之间的核对 | `verify.json`（引擎 timings 与客户端计时的差、启动设置是否进入引擎） |
| tune 的结果 | `sessions/*-tune-*/start-1/tune-presets.json`；各模型的汇总见 [configs/tuned/](configs/tuned/) |

流的原始数据（SSE 与思考全文）以及包含 PC 上全部进程的机器快照不公开。公开的日志中，主文件夹写作 `~`，主机名写作 `<host>`。

## 复现

测量耗时很长，因此作为 systemd 用户单元无人值守运行。步骤（准备环境、preflight、开始、监视、异常恢复、确定结果）见
[AGENTS.md](AGENTS.md)（英语），环境定义的写法见 [envs/README.md](envs/README.md)。

```bash
python3 -I scripts/envs.py list                                     # 与当前硬件匹配的环境
python3 -I scripts/build_cases.py                                    # 计划与用例一览（用例数与预估时间）
python3 scripts/preflight.py --phase all --steps "0,1,2,3,4a,4b,4c,4d,5"      # 开始前的检查
RUN_ID=<run id> STEPS="0 1 2 3 4a 4b 4c 4d 5" scripts/start_pipeline.sh       # 开始
```

## 许可证

- **代码**（脚本、页面模板、页面本身的代码）：[MIT License](LICENSE)
- **测量数据**（`published/`、`published/summary.csv`、`configs/tuned/`，以及页面上的数值与图表）：[CC BY 4.0](LICENSE-DATA.md)。
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
| [nvidia/Qwen3.8-Flash-Next-FP4-Local](https://huggingface.co/nvidia/Qwen3.8-Flash-Next-FP4-Local) | nvfp4 NVFP4-QAD（面向 FP4 的再训练；在本机转换为 Strata 的格式） |
