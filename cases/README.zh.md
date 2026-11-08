[日本語](README.md) · [English](README.en.md) · [中文](README.zh.md)

# Strata 基准测试 用例一览

按运行基准测试的硬件配置（GPU 与 RAM 的组合）分别保存计划和结果。点开环境名称即可查看该环境的全部用例。

**部门: 纯模型（无 harness）** — 模型与引擎本身的性能。不经过智能体 harness：由 runner 直接调用 strata launch 启动的引擎的 OpenAI 兼容 API（/v1/chat/completions）。不使用 tool call。

| 环境 | id | 用例 | 预估 h | 完成 | 失败 |
| --- | --- | ---: | ---: | ---: | ---: |
| [GeForce RTX 5070 · Core Ultra 5 235 · 64 GB RAM · SATA SSD](plain/rtx5070-cu5_235-64g-sata/README.zh.md) | `rtx5070-cu5_235-64g-sata` | 719 | 27 | 715 | 4 |
| [GeForce RTX 5090 · 128 GB RAM](plain/rtx5090-128g/README.zh.md) | `rtx5090-128g` | 1,388 | 25 | 1,328 | 0 |
