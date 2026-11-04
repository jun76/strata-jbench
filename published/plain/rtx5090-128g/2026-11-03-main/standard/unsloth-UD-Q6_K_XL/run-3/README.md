# Strata standard benchmark: NVIDIA GeForce RTX 5090

Protocol `strata-qwen38-thinking-v1-draft.1` (draft), run `20261103T131123Z-5d0bb7b5`, started 2026-11-03T13:11:23Z. **Status: complete.**

Written by `strata bench run`. The machine-readable result is [results.json](results.json); every request, its raw usage and timings and the client event offsets are in [outputs.jsonl](outputs.jsonl).

## Hardware and software

- GPU: NVIDIA GeForce RTX 5090 (31.8 GiB dedicated)
- CPU: Intel(R) Core(TM) i7-14700; RAM: 123.2 GiB
- Storage of the model files: nvme Fanxiang S880E 2TB (nvme)
- OS: Ubuntu 26.10 7.3.0-10-generic; drivers: gpu-driver 580.178.04; runtime: cuda 13.0
- Strata commit: `974074c549754029882c1cea1ce0e1e7674d7ba2`; engine 0.1.56; release build
- Background work: none (dedicated benchmark session)

## Model and configuration

- Model: qwen3.8-flash-next-unsloth-ud-q6_k_xl; quantization UD-Q6_K_XL; revision not measured; source revision not measured
- Files: `Qwen3.8-Flash-Next-UD-Q6_K_XL-00001-of-00006.gguf` `8bdc6bad55b6699f...`; `Qwen3.8-Flash-Next-UD-Q6_K_XL-00002-of-00006.gguf` `494ca4ed3dbf97bc...`; `Qwen3.8-Flash-Next-UD-Q6_K_XL-00003-of-00006.gguf` `34efd79a80a1ce54...`; `Qwen3.8-Flash-Next-UD-Q6_K_XL-00004-of-00006.gguf` `0ea4b599880a5a52...`; `Qwen3.8-Flash-Next-UD-Q6_K_XL-00005-of-00006.gguf` `9948e81ae8368144...`; `Qwen3.8-Flash-Next-UD-Q6_K_XL-00006-of-00006.gguf` `e4ae255234f42b18...`
- Track: **custom** (no notes given by the operator)
- Context 131072 tokens; server capacity 1 slot(s)
- Sampling: temperature 1.0, top_p 0.95, top_k 20, min_p 0.0, presence_penalty 0.0, repetition_penalty 1.0, reasoning_effort xhigh; thinking on, preserved
- Engine options: `config.json`; chat template: `provenance/chat_template.jinja`

## Method

The frozen requests of `bench/prompts/standard-v1` (corpus `e75eff8b9feea04f...`) were sent over loopback HTTP, streaming, one at a time, in this order: 1 warm-up (excluded), 3 repetitions of the short, 4K and 16K prompts, and the twelve sanity checks. Prompt and decode speed are the engine's own `timings`; time to first token is the client's monotonic clock from dispatch to the first nonempty reasoning, answer or tool-call delta. No request was retried. Time after the model loaded: 2 min 18 s.

## Results

| Case | Prompt tok/s | Decode tok/s | TTFT s | First answer s | Total s | Capped |
| --- | --- | --- | --- | --- | --- | --- |
| short | n/a | 66.6 (66.2-70.3) n=3 | 0.69 (0.55-0.70) n=3 | 1.82 (1.41-1.90) n=3 | 5.0 (4.8-5.1) n=3 | 0/3 |
| prompt-4k | 1070.2 (1069.7-1087.5) n=3 | 71.3 (70.6-73.6) n=3 | 3.85 (3.79-3.85) n=3 | 6.93 (6.79-7.08) n=2 | 11.0 (10.8-11.0) n=3 | 3/3 |
| prompt-16k | 2111.3 (2109.5-2112.0) n=3 | 68.0 (67.9-71.1) n=3 | 7.80 (7.79-7.80) n=3 | 13.59 (12.48-14.17) n=3 | 15.3 (15.0-15.3) n=3 | 3/3 |

Cells are median (min-max) n=samples. Short is a prompt of about 80 tokens: its prompt rate is dominated by the fixed cost of a request, so it is not shown; read prompt speed from prompt-4k and prompt-16k. Capped = requests that reached the 512-token cap, reasoning and answer together. A capped request's total time is the time to the cap, not to an answer, and it has no first-answer time when it was still reasoning.

| Phase | Planned | Completed | Truncated | Failed | Skipped |
| --- | ---: | ---: | ---: | ---: | ---: |
| warmup | 1 | 0 | 1 | 0 | 0 |
| performance | 9 | 3 | 6 | 0 | 0 |
| sanity | 12 | 12 | 0 | 0 | 0 |
| concurrency | 0 | 0 | 0 | 0 | 0 |

Sanity checks: **12 of 12**.

| Case | Result | Reason |
| --- | --- | --- |
| I1 | pass | the expected JSON value |
| I2 | pass | the expected JSON value |
| I3 | pass | the expected JSON value |
| I4 | pass | the exact expected text |
| R1 | pass | the exact expected text |
| R2 | pass | the exact expected text |
| R3 | pass | the exact expected text |
| R4 | pass | the expected JSON value |
| T1 | pass | the expected tool call |
| T2 | pass | the expected tool call |
| T3 | pass | the expected tool call |
| T4 | pass | the expected tool call |

## Failures, exclusions and limitations

- No request failed.
- Excluded from speed summaries: performance-prompt-4k-r3: first_answer_s is not available for this request
- Prompt-prefix reuse is the shared template prefix only; the cache was not emptied between requests, and the expert cache stays warm and evolves. These are not cold-model measurements.
- Output caps include reasoning; a request that reaches its cap is `truncated` and fails its sanity check.
- The runner cannot see other programs on the machine, the repeat-stop and loop-recovery switches of the server, or the quantization repository's revision; see `missing` in results.json for every value it could not read.
- The server had answered 1 request(s) before this run.
