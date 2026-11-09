[日本語](tier-4c.md) · [English](tier-4c.en.md) · [中文](tier-4c.zh.md)

[← 用例一览](README.zh.md)

# Tier 4c: 扩展范围的长文本（512K / 1M；基准模型、最小与最大的模型）

GeForce RTX 5070 · Core Ultra 5 235 · 64 GB RAM · SATA SSD · 24 个用例 / 72 个请求。其他参数（输入内容、测量内容、备注、seed、timeout、启动会话）见 [tier-4c.csv](tier-4c.csv)。

| 状态 | case id | model | context | 配置 | 启动选项（相对默认） | fixture | effort | temp | 并发 | 输入 token | 输出 cap | 次数 | 结果 | 证据 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| done | `T4c-qwen-IQ3_S-long-512K-q-d10` | qwen IQ3_S | 512K (YaRN 2) | baseline |  | long-512K | none | 0.7 | 1 | 524,288 | 512 | 3 | prefill 1933.1 / decode 38.5 / TTFT ms 271004.6 / 接受率 0.425 / 正确 2/3 | [2026-11-06-main](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/cases/T4c-qwen-IQ3_S-long-512K-q-d10/) |
| done | `T4c-qwen-IQ3_S-long-512K-q-d50` | qwen IQ3_S | 512K (YaRN 2) | baseline |  | long-512K | none | 0.7 | 1 | 524,288 | 512 | 3 | prefill 1504.0 / decode 51.5 / TTFT ms 7693.8 / 接受率 0.433 / 正确 3/3 | [2026-11-06-main](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/cases/T4c-qwen-IQ3_S-long-512K-q-d50/) |
| done | `T4c-qwen-IQ3_S-long-512K-q-d90` | qwen IQ3_S | 512K (YaRN 2) | baseline |  | long-512K | none | 0.7 | 1 | 524,288 | 512 | 3 | prefill 1500.5 / decode 72.3 / TTFT ms 7688.6 / 接受率 0.556 / 正确 3/3 | [2026-11-06-main](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/cases/T4c-qwen-IQ3_S-long-512K-q-d90/) |
| done | `T4c-qwen-IQ3_S-long-512K-q-multi` | qwen IQ3_S | 512K (YaRN 2) | baseline |  | long-512K | none | 0.7 | 1 | 524,288 | 512 | 3 | prefill 1504.2 / decode 90.7 / TTFT ms 7696.9 / 接受率 0.834 / 正确 3/3 | [2026-11-06-main](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/cases/T4c-qwen-IQ3_S-long-512K-q-multi/) |
| done | `T4c-qwen-IQ3_S-long-1M-q-d10` | qwen IQ3_S | 1M (YaRN 4) | baseline |  | long-1M | none | 0.7 | 1 | 1,048,576 | 512 | 3 | prefill 347.0 / decode 16.0 / TTFT ms 3023316.1 / 接受率 0.621 / 正确 3/3 | [2026-11-06-main](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/cases/T4c-qwen-IQ3_S-long-1M-q-d10/) |
| done | `T4c-qwen-IQ3_S-long-1M-q-d50` | qwen IQ3_S | 1M (YaRN 4) | baseline |  | long-1M | none | 0.7 | 1 | 1,048,576 | 512 | 3 | prefill 14.1 / decode 23.6 / TTFT ms 15192.6 / 接受率 0.571 / 正确 2/3 | [2026-11-06-main](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/cases/T4c-qwen-IQ3_S-long-1M-q-d50/) |
| done | `T4c-qwen-IQ3_S-long-1M-q-d90` | qwen IQ3_S | 1M (YaRN 4) | baseline |  | long-1M | none | 0.7 | 1 | 1,048,576 | 512 | 3 | prefill 13.9 / decode 28.3 / TTFT ms 14155.0 / 接受率 0.577 / 正确 3/3 | [2026-11-06-main](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/cases/T4c-qwen-IQ3_S-long-1M-q-d90/) |
| done | `T4c-qwen-IQ3_S-long-1M-q-multi` | qwen IQ3_S | 1M (YaRN 4) | baseline |  | long-1M | none | 0.7 | 1 | 1,048,576 | 512 | 3 | prefill 16.6 / decode 16.0 / TTFT ms 12745.8 / 接受率 0.766 / 正确 3/3 | [2026-11-06-main](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/cases/T4c-qwen-IQ3_S-long-1M-q-multi/) |
| planned | `T4c-gyro-Gyro-S-long-512K-q-d10` | gyro Gyro-S | 512K (YaRN 2) | baseline |  | long-512K | none | 0.7 | 1 | 524,288 | 512 | 3 |  |  |
| planned | `T4c-gyro-Gyro-S-long-512K-q-d50` | gyro Gyro-S | 512K (YaRN 2) | baseline |  | long-512K | none | 0.7 | 1 | 524,288 | 512 | 3 |  |  |
| planned | `T4c-gyro-Gyro-S-long-512K-q-d90` | gyro Gyro-S | 512K (YaRN 2) | baseline |  | long-512K | none | 0.7 | 1 | 524,288 | 512 | 3 |  |  |
| planned | `T4c-gyro-Gyro-S-long-512K-q-multi` | gyro Gyro-S | 512K (YaRN 2) | baseline |  | long-512K | none | 0.7 | 1 | 524,288 | 512 | 3 |  |  |
| planned | `T4c-gyro-Gyro-S-long-1M-q-d10` | gyro Gyro-S | 1M (YaRN 4) | baseline |  | long-1M | none | 0.7 | 1 | 1,048,576 | 512 | 3 |  |  |
| planned | `T4c-gyro-Gyro-S-long-1M-q-d50` | gyro Gyro-S | 1M (YaRN 4) | baseline |  | long-1M | none | 0.7 | 1 | 1,048,576 | 512 | 3 |  |  |
| planned | `T4c-gyro-Gyro-S-long-1M-q-d90` | gyro Gyro-S | 1M (YaRN 4) | baseline |  | long-1M | none | 0.7 | 1 | 1,048,576 | 512 | 3 |  |  |
| planned | `T4c-gyro-Gyro-S-long-1M-q-multi` | gyro Gyro-S | 1M (YaRN 4) | baseline |  | long-1M | none | 0.7 | 1 | 1,048,576 | 512 | 3 |  |  |
| planned | `T4c-gyro-Gyro-M-long-512K-q-d10` | gyro Gyro-M | 512K (YaRN 2) | baseline |  | long-512K | none | 0.7 | 1 | 524,288 | 512 | 3 |  |  |
| planned | `T4c-gyro-Gyro-M-long-512K-q-d50` | gyro Gyro-M | 512K (YaRN 2) | baseline |  | long-512K | none | 0.7 | 1 | 524,288 | 512 | 3 |  |  |
| planned | `T4c-gyro-Gyro-M-long-512K-q-d90` | gyro Gyro-M | 512K (YaRN 2) | baseline |  | long-512K | none | 0.7 | 1 | 524,288 | 512 | 3 |  |  |
| planned | `T4c-gyro-Gyro-M-long-512K-q-multi` | gyro Gyro-M | 512K (YaRN 2) | baseline |  | long-512K | none | 0.7 | 1 | 524,288 | 512 | 3 |  |  |
| planned | `T4c-gyro-Gyro-M-long-1M-q-d10` | gyro Gyro-M | 1M (YaRN 4) | baseline |  | long-1M | none | 0.7 | 1 | 1,048,576 | 512 | 3 |  |  |
| planned | `T4c-gyro-Gyro-M-long-1M-q-d50` | gyro Gyro-M | 1M (YaRN 4) | baseline |  | long-1M | none | 0.7 | 1 | 1,048,576 | 512 | 3 |  |  |
| planned | `T4c-gyro-Gyro-M-long-1M-q-d90` | gyro Gyro-M | 1M (YaRN 4) | baseline |  | long-1M | none | 0.7 | 1 | 1,048,576 | 512 | 3 |  |  |
| planned | `T4c-gyro-Gyro-M-long-1M-q-multi` | gyro Gyro-M | 1M (YaRN 4) | baseline |  | long-1M | none | 0.7 | 1 | 1,048,576 | 512 | 3 |  |  |
