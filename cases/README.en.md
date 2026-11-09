[日本語](README.md) · [English](README.en.md) · [中文](README.zh.md)

# Strata bench cases

The plan and the results are kept per hardware set-up (a GPU and an amount of RAM). Open an environment for all its cases.

**Division: Plain (no harness)** — The models and the engine themselves. No agent harness: the runner calls the OpenAI-compatible API (/v1/chat/completions) of the engine started by strata launch directly. No tool calls.

| environment | id | cases | est. h | done | failed |
| --- | --- | ---: | ---: | ---: | ---: |
| [GeForce RTX 5070 · Core Ultra 5 235 · 64 GB RAM · SATA SSD](plain/rtx5070-cu5_235-64g-sata/README.en.md) | `rtx5070-cu5_235-64g-sata` | 1,034 | 39 | 1,018 | 16 |
| [GeForce RTX 5090 · 128 GB RAM](plain/rtx5090-128g/README.en.md) | `rtx5090-128g` | 1,803 | 28 | 1,218 | 0 |
