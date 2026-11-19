# Sync-Strata jbench

[日本語](README.md) | [English](README.en.md) | **中文**

使用本地推理引擎 [Sync-Strata](https://github.com/hiruhiru2005/sync-strata) 测量 Qwen3.8-Flash-Next 的 Sync 量化模型。仓库提供计划、脚本和测量记录，便于复现。

## 部门

本分支记录 [Sync-Strata 纯模型部门（`plain-sync`）](divisions/README.md) 的结果。运行器直接调用 Sync-Strata 的 OpenAI 兼容 API，不经过智能体 harness。

## 查看结果

表中显示最新的三次运行，更早的结果折叠在下方。

| 查看 | 内容 |
| --- | --- |
| 📈 图表 | 下载 HTML 后在浏览器中打开，可查看截至该次运行结束时的结果，包括模型速度、输入长度与等待时间，以及测量时的温度、功耗和内存。页面链接包含全部数值的 `summary.csv` |
| 📋 用例列表 | 按环境和 Tier 提供 Markdown 与 CSV，记录各用例的条件、结果和证据链接 |
| 📁 证据 | 该次运行的请求记录、响应、汇总和引擎启动记录 |

图表与用例列表汇总截至该次运行结束时的结果。同一环境内重复测量同一用例时，采用排序靠后的 RUN_ID 所对应的结果。

<!-- published-runs:start (scripts/publish.py writes this list) -->
| 测量完成 | 环境 | RUN_ID | Tier | 用例（done / 全部） | 内容 | 查看 |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-11-19 16:39 | GeForce RTX 5070 · Core Ultra 5 235 · 64 GB RAM · SATA SSD | `2026-11-19-sync-r10` | 1 | 54 / 54 | 在 Sync-Strata 0.1.1 上测量 Sync-XS、Sync-S 和 Sync-M 的 Tier 1，使用 R10（关闭 tail skip）、128K 上下文、k8v4 KV 和 MTP。54 个用例、162 个请求全部成功。 | [📈](snapshots/plain-sync/rtx5070-cu5_235-64g-sata/2026-11-19-sync-r10/index.html "图表") [📋](https://github.com/jun76/strata-jbench/blob/run/plain-sync/rtx5070-cu5_235-64g-sata/2026-11-19-sync-r10/cases/plain-sync/rtx5070-cu5_235-64g-sata/README.zh.md "用例一览") [📁](published/plain-sync/rtx5070-cu5_235-64g-sata/2026-11-19-sync-r10/ "证据") |
<!-- published-runs:end -->

## 测量了什么

计划按测量项目划分 Tier。结果表列出每次运行涉及的 Tier，用例列表和启动记录给出采样、tail skip、上下文长度等条件。用例由 [scripts/build_cases.py](scripts/build_cases.py) 定义。

### 测量方法

- [Sync-Strata 集成](scripts/sync_engine.py) 通过 `sync up --api-only` 在专用端口启动引擎。[运行器](scripts/bench_runner.py) 调用流式 `POST /v1/chat/completions`，记录 prefill、decode 和首字延迟（TTFT）。
- 速度用例使用文章、JSON、代码和照抄等短提示测量 decode，并用不同长度的固定输入测量 prefill 和 TTFT。每个用例使用 seed 1、2、3，图表显示中位数和范围。
- 运行器使用固定的[提示词](prompts/)，在请求中指定采样和 thinking，并加上唯一的前缀标记以避免复用早先请求的缓存。
- 每次运行单独保存 Sync 设置和进程状态，并读取预先安装的模型文件。测量期间避开下载和其他高负载任务。

### 测量环境

结果按硬件配置归档，包括 GPU、CPU、RAM 和模型存储。图表可切换环境，并在多个环境有数据时比较条件相同的用例。每次运行的 `machine.json` 记录驱动程序、功耗上限和 Sync-Strata 版本。参见[环境定义](envs/README.md)。

## 数据位置

| 内容 | 位置 |
| --- | --- |
| 运行证据 | `published/plain-sync/<环境>/<RUN_ID>/` |
| 用例列表 | `cases/plain-sync/<环境>/` |
| 图表与汇总 CSV | `snapshots/plain-sync/<环境>/<RUN_ID>/` |
| 用例汇总与响应 | 运行目录内的 `cases/<case id>/summary.json`、`requests.jsonl`、`responses/` |
| 启动配置、引擎日志和资源采样 | 运行目录内的 `sessions/<session>/start-N/` |
| 机器配置与模型发布信息 | `machine.json`、`sync-models.json` |
| 温度与功耗变化 | `stats/thermal.csv` |
| 运行日志与验证结果 | `queue.log`、`runner.log`、`verify.json` |

用于发布的日志将主目录替换为 `~`，将主机名替换为 `<host>`。

### 只留在本机的内容

| 内容 | 位置 |
| --- | --- |
| 工作结果 | `results/` |
| 原始流与完整思考内容 | 各用例的 `raw/` |
| Sync-Strata 的运行设置和状态 | 运行目录内的 `sync-home/` |
| 全机进程、CPU、内存和磁盘快照 | 运行目录内的 `stats/snapshots.jsonl.gz`。可在 `bench.json` 中设 `"stats": false` 关闭采集 |
| 计划、预览、运行状态与预检 | `plan/`、`preview/`、`run-status/` |
| 本机设置 | 仓库根目录的 `bench.json` 和 `envs/<环境>/env.json` |

## 复现

设置 Sync-Strata，并通过 Sync-Strata 安装所需模型包和共享文件。当前适配器使用 `~/sync-strata/.sync-local/` 下的运行环境及模型设置。创建与硬件匹配的[环境](envs/README.md)，并在 `bench.json` 中选择 RUN_ID 与测试范围。

```bash
python3 -I scripts/envs.py list          # 匹配的硬件环境
python3 -I scripts/bench.py config       # 设置和默认值
python3 -I scripts/bench.py plan         # 选定的用例与预计耗时
python3 -I scripts/acquire.py check     # 检查模型包和共享文件
python3 -I scripts/bench.py start        # 启动 supervisor 并执行预检
python3 -I scripts/bench.py status       # 查看进度
python3 -I scripts/bench.py stop         # 停止，之后可用相同 RUN_ID 恢复
```

supervisor 独立于终端运行。预检、监控、故障恢复和整理结果的流程见 [AGENTS.md](AGENTS.md)。

## 许可证

- 代码采用 [MIT License](LICENSE)。
- 测量数据和图表采用 [CC BY 4.0](LICENSE-DATA.md)。引用时请注明 strata-jbench、仓库链接、环境和 RUN_ID。
- 模型与引擎遵循各自的许可证。

## 参考与致谢

- [Sync-Strata](https://github.com/hiruhiru2005/sync-strata) 提供推理引擎和 Sync 量化模型。
- [Qwen3.8-Flash-Next](https://huggingface.co/Qwen/Qwen3.8-Flash-Next) 是基础模型。

| 模型 | 发布地址 |
| --- | --- |
| Sync-XS | [hiru2005/Sync-XS](https://huggingface.co/hiru2005/Sync-XS) |
| Sync-S | [hiru2005/Sync-S](https://huggingface.co/hiru2005/Sync-S) |
| Sync-M | [sync-strata/Sync-M](https://huggingface.co/sync-strata/Sync-M) |
