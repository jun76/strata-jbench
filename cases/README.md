[日本語](README.md) · [English](README.en.md) · [中文](README.zh.md)

# Strata ベンチ ケース一覧

ベンチを回すハードウェア構成（GPU と RAM の組み合わせ）ごとに、計画と結果を分けて持つ。環境の名前を開くと、その環境の全ケースの一覧。

**部門: プレーン（ハーネスなし）** — モデルとエンジンそのものの性能。エージェント用のハーネスは通さず、strata launch で立てたエンジンの OpenAI 互換 API（/v1/chat/completions）をランナーが直接呼ぶ。tool call は使わない。

| 環境 | id | ケース | 見積 h | 完了 | 失敗 |
| --- | --- | ---: | ---: | ---: | ---: |
| [GeForce RTX 5090 · 128 GB RAM](plain/rtx5090-128g/README.md) | `rtx5090-128g` | 1,352 | 25 | 1,352 | 0 |
