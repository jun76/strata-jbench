# Strata standard benchmark: NVIDIA GeForce RTX 5090

Protocol `strata-qwen38-thinking-v1-draft.1` (draft), run `20261125T214329Z-5eb0e4c2`, started 2026-11-25T21:43:29Z. **Status: nonconforming.**

Written by `strata bench run`. The machine-readable result is [results.json](results.json); every request, its raw usage and timings and the client event offsets are in [outputs.jsonl](outputs.jsonl).

This run is not a complete standard result:

- no model file could be hashed
- performance-prompt-4k-r1 measured 2795 prompt tokens, outside 2% of its target
- performance-prompt-16k-r1 measured 11206 prompt tokens, outside 2% of its target
- performance-prompt-4k-r2 measured 2795 prompt tokens, outside 2% of its target
- performance-prompt-16k-r2 measured 11206 prompt tokens, outside 2% of its target
- performance-prompt-4k-r3 measured 2795 prompt tokens, outside 2% of its target
- performance-prompt-16k-r3 measured 11206 prompt tokens, outside 2% of its target
- sanity-R1 measured 2789 prompt tokens, outside 2% of its target
- sanity-R2 measured 2790 prompt tokens, outside 2% of its target
- sanity-R3 measured 11200 prompt tokens, outside 2% of its target
- sanity-R4 measured 11207 prompt tokens, outside 2% of its target

## Hardware and software

- GPU: NVIDIA GeForce RTX 5090 (31.8 GiB dedicated)
- CPU: Intel(R) Core(TM) i7-14700; RAM: 123.2 GiB
- Storage of the model files: not measured
- OS: Ubuntu 26.10 7.3.0-10-generic; drivers: gpu-driver 580.178.04; runtime: cuda 13.0
- Strata commit: `d46f5f268f8ed797e83a5c63a69bffbd7a581cf6`; engine hy4-serve-0; release build
- Background work: none (dedicated benchmark session)

## Model and configuration

- Model: hy4-flash-sq-64; quantization not measured; revision not measured; source revision not measured
- Files: not measured
- Track: **custom** (no notes given by the operator)
- Context 131072 tokens; server capacity 1 slot(s)
- Sampling: temperature 1.0, top_p 0.95, top_k 20, min_p 0.0, presence_penalty 0.0, repetition_penalty 1.0, reasoning_effort xhigh; thinking on, preserved
- Engine options: `config.json`; chat template: `provenance/chat_template.jinja`

## Method

The frozen requests of `bench/prompts/standard-v1` (corpus `e75eff8b9feea04f...`) were sent over loopback HTTP, streaming, one at a time, in this order: 1 warm-up (excluded), 3 repetitions of the short, 4K and 16K prompts, and the twelve sanity checks. Prompt and decode speed are the engine's own `timings`; time to first token is the client's monotonic clock from dispatch to the first nonempty reasoning, answer or tool-call delta. No request was retried. Time after the model loaded: 8 min 20 s.

## Results

| Case | Prompt tok/s | Decode tok/s | TTFT s | First answer s | Total s | Capped |
| --- | --- | --- | --- | --- | --- | --- |
| short | n/a | 15.3 (15.0-16.3) n=3 | 0.67 (0.58-0.69) n=3 | 27.67 (23.00-27.99) n=3 | 34.1 (32.0-34.7) n=3 | 3/3 |
| prompt-4k | 645.0 (616.7-667.3) n=3 | 14.0 (14.0-15.0) n=3 | 4.34 (4.19-4.54) n=3 | 33.88 (33.58-34.17) n=2 | 40.7 (38.4-41.2) n=3 | 3/3 |
| prompt-16k | 821.9 (810.1-823.0) n=3 | 14.9 (14.4-15.3) n=3 | 13.65 (13.63-13.85) n=3 | 44.37 (40.12-48.62) n=2 | 48.1 (47.0-49.4) n=3 | 3/3 |

Cells are median (min-max) n=samples. Short is a prompt of about 80 tokens: its prompt rate is dominated by the fixed cost of a request, so it is not shown; read prompt speed from prompt-4k and prompt-16k. Capped = requests that reached the 512-token cap, reasoning and answer together. A capped request's total time is the time to the cap, not to an answer, and it has no first-answer time when it was still reasoning.

| Phase | Planned | Completed | Truncated | Failed | Skipped |
| --- | ---: | ---: | ---: | ---: | ---: |
| warmup | 1 | 0 | 1 | 0 | 0 |
| performance | 9 | 0 | 9 | 0 | 0 |
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
- Excluded from speed summaries: performance-prompt-16k-r3: first_answer_s is not available for this request
- Excluded from speed summaries: performance-prompt-4k-r2: first_answer_s is not available for this request
- Prompt-prefix reuse is the shared template prefix only; the cache was not emptied between requests, and the expert cache stays warm and evolves. These are not cold-model measurements.
- Output caps include reasoning; a request that reaches its cap is `truncated` and fails its sanity check.
- The runner cannot see other programs on the machine, the repeat-stop and loop-recovery switches of the server, or the quantization repository's revision; see `missing` in results.json for every value it could not read.
- The server had answered 1 request(s) before this run.
