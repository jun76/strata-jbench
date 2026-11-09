# Strata standard benchmark: NVIDIA GeForce RTX 5070

Protocol `strata-qwen38-thinking-v1-draft.1` (draft), run `20261107T024700Z-8995e9ee`, started 2026-11-07T02:47:00Z. **Status: complete.**

Written by `strata bench run`. The machine-readable result is [results.json](results.json); every request, its raw usage and timings and the client event offsets are in [outputs.jsonl](outputs.jsonl).

## Hardware and software

- GPU: NVIDIA GeForce RTX 5070 (11.9 GiB dedicated)
- CPU: Intel(R) Core(TM) Ultra 5 235; RAM: 60.9 GiB
- Storage of the model files: ssd SanDisk SD9SB8W1T001122 (sata)
- OS: Ubuntu 26.04.1 LTS 7.0.0-42-generic; drivers: gpu-driver 595.99.02; runtime: cuda 13.2
- Strata commit: `c3b3f5035506f3e966f1b4b7b188aeaabae92f1d`; engine 0.1.57; release build
- Background work: none (dedicated benchmark session)

## Model and configuration

- Model: qwen3.8-flash-next-unsloth-ud-q2_0; quantization UD-Q2_0; revision not measured; source revision not measured
- Files: `Qwen3.8-Flash-Next-UD-Q2_0-00001-of-00003.gguf` `38803c4e8d130771...`; `Qwen3.8-Flash-Next-UD-Q2_0-00002-of-00003.gguf` `57af20207d5f18fa...`; `Qwen3.8-Flash-Next-UD-Q2_0-00003-of-00003.gguf` `05716382c280d999...`
- Track: **custom** (no notes given by the operator)
- Context 131072 tokens; server capacity 1 slot(s)
- Sampling: temperature 1.0, top_p 0.95, top_k 20, min_p 0.0, presence_penalty 0.0, repetition_penalty 1.0, reasoning_effort xhigh; thinking on, preserved
- Engine options: `config.json`; chat template: `provenance/chat_template.jinja`

## Method

The frozen requests of `bench/prompts/standard-v1` (corpus `e75eff8b9feea04f...`) were sent over loopback HTTP, streaming, one at a time, in this order: 1 warm-up (excluded), 3 repetitions of the short, 4K and 16K prompts, and the twelve sanity checks. Prompt and decode speed are the engine's own `timings`; time to first token is the client's monotonic clock from dispatch to the first nonempty reasoning, answer or tool-call delta. No request was retried. Time after the model loaded: 1 min 48 s.

## Results

| Case | Prompt tok/s | Decode tok/s | TTFT s | First answer s | Total s | Capped |
| --- | --- | --- | --- | --- | --- | --- |
| short | n/a | 90.2 (88.1-94.9) n=3 | 0.55 (0.43-0.58) n=3 | 1.49 (1.15-2.24) n=3 | 4.8 (4.1-6.0) n=3 | 1/3 |
| prompt-4k | 2230.3 (2182.1-2306.2) n=3 | 88.9 (87.0-91.7) n=3 | 1.86 (1.80-1.90) n=3 | 4.01 (3.94-4.34) n=3 | 7.5 (7.5-7.7) n=3 | 3/3 |
| prompt-16k | 2547.8 (2541.9-2555.2) n=3 | 89.0 (80.2-89.5) n=3 | 6.46 (6.44-6.47) n=3 | 9.12 (8.81-12.79) n=3 | 12.2 (12.2-12.8) n=3 | 3/3 |

Cells are median (min-max) n=samples. Short is a prompt of about 80 tokens: its prompt rate is dominated by the fixed cost of a request, so it is not shown; read prompt speed from prompt-4k and prompt-16k. Capped = requests that reached the 512-token cap, reasoning and answer together. A capped request's total time is the time to the cap, not to an answer, and it has no first-answer time when it was still reasoning.

| Phase | Planned | Completed | Truncated | Failed | Skipped |
| --- | ---: | ---: | ---: | ---: | ---: |
| warmup | 1 | 0 | 1 | 0 | 0 |
| performance | 9 | 2 | 7 | 0 | 0 |
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
- Prompt-prefix reuse is the shared template prefix only; the cache was not emptied between requests, and the expert cache stays warm and evolves. These are not cold-model measurements.
- Output caps include reasoning; a request that reaches its cap is `truncated` and fails its sanity check.
- The runner cannot see other programs on the machine, the repeat-stop and loop-recovery switches of the server, or the quantization repository's revision; see `missing` in results.json for every value it could not read.
- The server had answered 1 request(s) before this run.
