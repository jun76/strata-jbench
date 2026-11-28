# Strata standard benchmark: NVIDIA GeForce RTX 5090

Protocol `strata-qwen38-thinking-v1-draft.1` (draft), run `20261128T002429Z-0e63b8a9`, started 2026-11-28T00:24:29Z. **Status: nonconforming.**

Written by `strata bench run`. The machine-readable result is [results.json](results.json); every request, its raw usage and timings and the client event offsets are in [outputs.jsonl](outputs.jsonl).

This run is not a complete standard result:

- performance-prompt-4k-r1 measured 3423 prompt tokens, outside 2% of its target
- performance-prompt-16k-r1 measured 13775 prompt tokens, outside 2% of its target
- performance-prompt-4k-r2 measured 3423 prompt tokens, outside 2% of its target
- performance-prompt-16k-r2 measured 13775 prompt tokens, outside 2% of its target
- performance-prompt-4k-r3 measured 3423 prompt tokens, outside 2% of its target
- performance-prompt-16k-r3 measured 13775 prompt tokens, outside 2% of its target
- sanity-R1 measured 3421 prompt tokens, outside 2% of its target
- sanity-R2 measured 3422 prompt tokens, outside 2% of its target
- sanity-R3 measured 13773 prompt tokens, outside 2% of its target
- sanity-R4 measured 13777 prompt tokens, outside 2% of its target

## Hardware and software

- GPU: NVIDIA GeForce RTX 5090 (31.8 GiB dedicated)
- CPU: Intel(R) Core(TM) i7-14700; RAM: 123.2 GiB
- Storage of the model files: nvme CSSD-M2RF72LT2000GB (nvme)
- OS: Ubuntu 26.10 7.3.0-10-generic; drivers: gpu-driver 580.178.04; runtime: cuda 13.0
- Strata commit: `4560d03793482ef367294cfbd86a4df8d5679e72`; engine strata-inkling-0.1.70; release build
- Background work: none (dedicated benchmark session)

## Model and configuration

- Model: inkling-2-mini-gsq-rco-iq3_s; quantization IQ3_S; revision not measured; source revision not measured
- Files: `Inkling-2-Mini-GSQ-RCO-IQ3_S.gguf` `8a3515374c3cd9b6...`
- Track: **custom** (no notes given by the operator)
- Context 131072 tokens; server capacity 1 slot(s)
- Sampling: temperature 1.0, top_p 0.95, top_k 20, min_p 0.0, presence_penalty 0.0, repetition_penalty 1.0, reasoning_effort xhigh; thinking on, preserved
- Engine options: `config.json`; chat template: `provenance/chat_template.jinja`

## Method

The frozen requests of `bench/prompts/standard-v1` (corpus `e75eff8b9feea04f...`) were sent over loopback HTTP, streaming, one at a time, in this order: 1 warm-up (excluded), 3 repetitions of the short, 4K and 16K prompts, and the twelve sanity checks. Prompt and decode speed are the engine's own `timings`; time to first token is the client's monotonic clock from dispatch to the first nonempty reasoning, answer or tool-call delta. No request was retried. Time after the model loaded: 1 min 21 s.

## Results

| Case | Prompt tok/s | Decode tok/s | TTFT s | First answer s | Total s | Capped |
| --- | --- | --- | --- | --- | --- | --- |
| short | n/a | 182.6 (173.7-184.5) n=3 | 0.07 (0.07-0.07) n=3 | 1.71 (1.50-1.72) n=3 | 2.9 (2.8-3.1) n=3 | 3/3 |
| prompt-4k | 2026.8 (1856.8-2038.0) n=3 | 164.4 (156.9-189.1) n=3 | 1.70 (1.69-1.71) n=3 | 3.35 (3.34-3.38) n=3 | 4.7 (4.5-4.9) n=3 | 3/3 |
| prompt-16k | 1968.4 (1964.2-1987.3) n=3 | 159.3 (149.1-162.8) n=3 | 7.00 (6.94-7.02) n=3 | 8.73 (8.57-8.79) n=3 | 10.1 (9.8-10.4) n=3 | 2/3 |

Cells are median (min-max) n=samples. Short is a prompt of about 80 tokens: its prompt rate is dominated by the fixed cost of a request, so it is not shown; read prompt speed from prompt-4k and prompt-16k. Capped = requests that reached the 512-token cap, reasoning and answer together. A capped request's total time is the time to the cap, not to an answer, and it has no first-answer time when it was still reasoning.

| Phase | Planned | Completed | Truncated | Failed | Skipped |
| --- | ---: | ---: | ---: | ---: | ---: |
| warmup | 1 | 0 | 1 | 0 | 0 |
| performance | 9 | 1 | 8 | 0 | 0 |
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
