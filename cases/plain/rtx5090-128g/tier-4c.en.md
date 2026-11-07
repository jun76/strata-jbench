[日本語](tier-4c.md) · [English](tier-4c.en.md) · [中文](tier-4c.zh.md)

[← cases](README.en.md)

# Tier 4c: long inputs in the extended range (512K / 1M; the reference model, the smallest and the largest)

GeForce RTX 5090 · 128 GB RAM · 24 cases / 72 requests. The other parameters (input, measures, notes, seeds, timeout, launch session) are in [tier-4c.csv](tier-4c.csv).

| status | case id | model | context | config | launch options (vs. default) | fixture | effort | temp | concurrency | input tokens | output cap | runs | result | evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| done | `T4c-qwen-IQ3_S-long-512K-q-d10` | qwen IQ3_S | 512K (YaRN 2) | baseline |  | long-512K | none | 0.7 | 1 | 524,288 | 512 | 3 | prefill 4409.7 / decode 110.5 / TTFT ms 118967.5 / acceptance 0.5 / correct 3/3 | [2026-11-04-long](../../../published/plain/rtx5090-128g/2026-11-04-long/cases/T4c-qwen-IQ3_S-long-512K-q-d10/) |
| done | `T4c-qwen-IQ3_S-long-512K-q-d50` | qwen IQ3_S | 512K (YaRN 2) | baseline |  | long-512K | none | 0.7 | 1 | 524,288 | 512 | 3 | prefill 3306.1 / decode 163.6 / TTFT ms 4916.5 / acceptance 0.739 / correct 3/3 | [2026-11-04-long](../../../published/plain/rtx5090-128g/2026-11-04-long/cases/T4c-qwen-IQ3_S-long-512K-q-d50/) |
| done | `T4c-qwen-IQ3_S-long-512K-q-d90` | qwen IQ3_S | 512K (YaRN 2) | baseline |  | long-512K | none | 0.7 | 1 | 524,288 | 512 | 3 | prefill 3304.7 / decode 162.9 / TTFT ms 4922.4 / acceptance 0.655 / correct 3/3 | [2026-11-04-long](../../../published/plain/rtx5090-128g/2026-11-04-long/cases/T4c-qwen-IQ3_S-long-512K-q-d90/) |
| done | `T4c-qwen-IQ3_S-long-512K-q-multi` | qwen IQ3_S | 512K (YaRN 2) | baseline |  | long-512K | none | 0.7 | 1 | 524,288 | 512 | 3 | prefill 3309.7 / decode 221.8 / TTFT ms 4915.9 / acceptance 0.743 / correct 3/3 | [2026-11-04-long](../../../published/plain/rtx5090-128g/2026-11-04-long/cases/T4c-qwen-IQ3_S-long-512K-q-multi/) |
| done | `T4c-qwen-IQ3_S-long-1M-q-d10` | qwen IQ3_S | 1M (YaRN 4) | baseline |  | long-1M | none | 0.7 | 1 | 1,048,576 | 512 | 3 | prefill 3415.5 / decode 97.0 / TTFT ms 307205.5 / acceptance 0.629 / correct 2/3 | [2026-11-04-long](../../../published/plain/rtx5090-128g/2026-11-04-long/cases/T4c-qwen-IQ3_S-long-1M-q-d10/) |
| done | `T4c-qwen-IQ3_S-long-1M-q-d50` | qwen IQ3_S | 1M (YaRN 4) | baseline |  | long-1M | none | 0.7 | 1 | 1,048,576 | 512 | 3 | prefill 2266.4 / decode 98.0 / TTFT ms 7282.4 / acceptance 0.552 / correct 3/3 | [2026-11-04-long](../../../published/plain/rtx5090-128g/2026-11-04-long/cases/T4c-qwen-IQ3_S-long-1M-q-d50/) |
| done | `T4c-qwen-IQ3_S-long-1M-q-d90` | qwen IQ3_S | 1M (YaRN 4) | baseline |  | long-1M | none | 0.7 | 1 | 1,048,576 | 512 | 3 | prefill 2268.2 / decode 117.5 / TTFT ms 7277.8 / acceptance 0.659 / correct 3/3 | [2026-11-04-long](../../../published/plain/rtx5090-128g/2026-11-04-long/cases/T4c-qwen-IQ3_S-long-1M-q-d90/) |
| done | `T4c-qwen-IQ3_S-long-1M-q-multi` | qwen IQ3_S | 1M (YaRN 4) | baseline |  | long-1M | none | 0.7 | 1 | 1,048,576 | 512 | 3 | prefill 2269.8 / decode 144.9 / TTFT ms 7282.6 / acceptance 0.736 / correct 3/3 | [2026-11-04-long](../../../published/plain/rtx5090-128g/2026-11-04-long/cases/T4c-qwen-IQ3_S-long-1M-q-multi/) |
| planned | `T4c-gyro-Gyro-S-long-512K-q-d10` | gyro Gyro-S | 512K (YaRN 2) | baseline |  | long-512K | none | 0.7 | 1 | 524,288 | 512 | 3 |  |  |
| planned | `T4c-gyro-Gyro-S-long-512K-q-d50` | gyro Gyro-S | 512K (YaRN 2) | baseline |  | long-512K | none | 0.7 | 1 | 524,288 | 512 | 3 |  |  |
| planned | `T4c-gyro-Gyro-S-long-512K-q-d90` | gyro Gyro-S | 512K (YaRN 2) | baseline |  | long-512K | none | 0.7 | 1 | 524,288 | 512 | 3 |  |  |
| planned | `T4c-gyro-Gyro-S-long-512K-q-multi` | gyro Gyro-S | 512K (YaRN 2) | baseline |  | long-512K | none | 0.7 | 1 | 524,288 | 512 | 3 |  |  |
| planned | `T4c-gyro-Gyro-S-long-1M-q-d10` | gyro Gyro-S | 1M (YaRN 4) | baseline |  | long-1M | none | 0.7 | 1 | 1,048,576 | 512 | 3 |  |  |
| planned | `T4c-gyro-Gyro-S-long-1M-q-d50` | gyro Gyro-S | 1M (YaRN 4) | baseline |  | long-1M | none | 0.7 | 1 | 1,048,576 | 512 | 3 |  |  |
| planned | `T4c-gyro-Gyro-S-long-1M-q-d90` | gyro Gyro-S | 1M (YaRN 4) | baseline |  | long-1M | none | 0.7 | 1 | 1,048,576 | 512 | 3 |  |  |
| planned | `T4c-gyro-Gyro-S-long-1M-q-multi` | gyro Gyro-S | 1M (YaRN 4) | baseline |  | long-1M | none | 0.7 | 1 | 1,048,576 | 512 | 3 |  |  |
| planned | `T4c-unsloth-Q8_0-long-512K-q-d10` | unsloth Q8_0 | 512K (YaRN 2) | baseline |  | long-512K | none | 0.7 | 1 | 524,288 | 512 | 3 |  |  |
| planned | `T4c-unsloth-Q8_0-long-512K-q-d50` | unsloth Q8_0 | 512K (YaRN 2) | baseline |  | long-512K | none | 0.7 | 1 | 524,288 | 512 | 3 |  |  |
| planned | `T4c-unsloth-Q8_0-long-512K-q-d90` | unsloth Q8_0 | 512K (YaRN 2) | baseline |  | long-512K | none | 0.7 | 1 | 524,288 | 512 | 3 |  |  |
| planned | `T4c-unsloth-Q8_0-long-512K-q-multi` | unsloth Q8_0 | 512K (YaRN 2) | baseline |  | long-512K | none | 0.7 | 1 | 524,288 | 512 | 3 |  |  |
| planned | `T4c-unsloth-Q8_0-long-1M-q-d10` | unsloth Q8_0 | 1M (YaRN 4) | baseline |  | long-1M | none | 0.7 | 1 | 1,048,576 | 512 | 3 |  |  |
| planned | `T4c-unsloth-Q8_0-long-1M-q-d50` | unsloth Q8_0 | 1M (YaRN 4) | baseline |  | long-1M | none | 0.7 | 1 | 1,048,576 | 512 | 3 |  |  |
| planned | `T4c-unsloth-Q8_0-long-1M-q-d90` | unsloth Q8_0 | 1M (YaRN 4) | baseline |  | long-1M | none | 0.7 | 1 | 1,048,576 | 512 | 3 |  |  |
| planned | `T4c-unsloth-Q8_0-long-1M-q-multi` | unsloth Q8_0 | 1M (YaRN 4) | baseline |  | long-1M | none | 0.7 | 1 | 1,048,576 | 512 | 3 |  |  |
