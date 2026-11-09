[日本語](tier-4c.md) · [English](tier-4c.en.md) · [中文](tier-4c.zh.md)

[← cases](README.en.md)

# Tier 4c: long inputs in the extended range (512K / 1M; the reference model, the smallest and the largest)

GeForce RTX 5070 · Core Ultra 5 235 · 64 GB RAM · SATA SSD · 24 cases / 72 requests. The other parameters (input, measures, notes, seeds, timeout, launch session) are in [tier-4c.csv](tier-4c.csv).

| status | case id | model | context | config | launch options (vs. default) | fixture | effort | temp | concurrency | input tokens | output cap | runs | result | evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| done | `T4c-qwen-IQ3_S-long-512K-q-d10` | qwen IQ3_S | 512K (YaRN 2) | baseline |  | long-512K | none | 0.7 | 1 | 524,288 | 512 | 3 | prefill 1933.1 / decode 38.5 / TTFT ms 271004.6 / acceptance 0.425 / correct 2/3 | [2026-11-06-main](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/cases/T4c-qwen-IQ3_S-long-512K-q-d10/) |
| done | `T4c-qwen-IQ3_S-long-512K-q-d50` | qwen IQ3_S | 512K (YaRN 2) | baseline |  | long-512K | none | 0.7 | 1 | 524,288 | 512 | 3 | prefill 1504.0 / decode 51.5 / TTFT ms 7693.8 / acceptance 0.433 / correct 3/3 | [2026-11-06-main](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/cases/T4c-qwen-IQ3_S-long-512K-q-d50/) |
| done | `T4c-qwen-IQ3_S-long-512K-q-d90` | qwen IQ3_S | 512K (YaRN 2) | baseline |  | long-512K | none | 0.7 | 1 | 524,288 | 512 | 3 | prefill 1500.5 / decode 72.3 / TTFT ms 7688.6 / acceptance 0.556 / correct 3/3 | [2026-11-06-main](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/cases/T4c-qwen-IQ3_S-long-512K-q-d90/) |
| done | `T4c-qwen-IQ3_S-long-512K-q-multi` | qwen IQ3_S | 512K (YaRN 2) | baseline |  | long-512K | none | 0.7 | 1 | 524,288 | 512 | 3 | prefill 1504.2 / decode 90.7 / TTFT ms 7696.9 / acceptance 0.834 / correct 3/3 | [2026-11-06-main](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/cases/T4c-qwen-IQ3_S-long-512K-q-multi/) |
| done | `T4c-qwen-IQ3_S-long-1M-q-d10` | qwen IQ3_S | 1M (YaRN 4) | baseline |  | long-1M | none | 0.7 | 1 | 1,048,576 | 512 | 3 | prefill 347.0 / decode 16.0 / TTFT ms 3023316.1 / acceptance 0.621 / correct 3/3 | [2026-11-06-main](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/cases/T4c-qwen-IQ3_S-long-1M-q-d10/) |
| done | `T4c-qwen-IQ3_S-long-1M-q-d50` | qwen IQ3_S | 1M (YaRN 4) | baseline |  | long-1M | none | 0.7 | 1 | 1,048,576 | 512 | 3 | prefill 14.1 / decode 23.6 / TTFT ms 15192.6 / acceptance 0.571 / correct 2/3 | [2026-11-06-main](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/cases/T4c-qwen-IQ3_S-long-1M-q-d50/) |
| done | `T4c-qwen-IQ3_S-long-1M-q-d90` | qwen IQ3_S | 1M (YaRN 4) | baseline |  | long-1M | none | 0.7 | 1 | 1,048,576 | 512 | 3 | prefill 13.9 / decode 28.3 / TTFT ms 14155.0 / acceptance 0.577 / correct 3/3 | [2026-11-06-main](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/cases/T4c-qwen-IQ3_S-long-1M-q-d90/) |
| done | `T4c-qwen-IQ3_S-long-1M-q-multi` | qwen IQ3_S | 1M (YaRN 4) | baseline |  | long-1M | none | 0.7 | 1 | 1,048,576 | 512 | 3 | prefill 16.6 / decode 16.0 / TTFT ms 12745.8 / acceptance 0.766 / correct 3/3 | [2026-11-06-main](../../../published/plain/rtx5070-cu5_235-64g-sata/2026-11-06-main/cases/T4c-qwen-IQ3_S-long-1M-q-multi/) |
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
