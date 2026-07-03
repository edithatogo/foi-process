# Track 14 — Rust-Backed Tooling and Hot-Path Modernization — Review

**Status:** Complete (experiments reviewed; no broad production replacement promoted)  
**Date:** 2026-06-23  
**Reviewer:** codex (implementation + review follow-up)

## Findings

### Verification Matrix

- Serializer benchmark script is present and executable:
  - `nlp-policy-nz/scripts/benchmark_msgspec_orjson.py`
  - Evidence written to `nlp-policy-nz/.tmp/track14_msgspec_orjson_benchmark.json`
- Tokenizer benchmark script is present and executable:
  - `nlp-policy-nz/scripts/benchmark_tokenizers_chunking.py`
  - Evidence written to `nlp-policy-nz/.tmp/track14_tokenizers_chunking_benchmark.json`
- Selectolax parser benchmark script is present and executable:
  - `corpus-cases-medilegal-nz/scripts/benchmark_selectolax_parser.py`
  - Evidence written to `corpus-cases-medilegal-nz/.tmp/track14_selectolax_parser_benchmark.json`
- Contract test for parser benchmark exists and passes:
  - `corpus-cases-medilegal-nz/tests/test_track14_selectolax_benchmark.py`
- Dependency-enabled reruns completed after installing optional wheels into the
  active Python environment:
  - `orjson==3.11.9`
  - `selectolax==0.4.10`

### Outcome Notes

1. `msgspec_json` is measured and faster than stdlib JSON in the latest local serializer fixture: 1.807 ms average versus 3.856 ms.
2. `orjson` is measured and faster than stdlib JSON in the latest local serializer fixture: 2.814 ms average versus 3.856 ms.
3. `tokenizers` is measured and faster than the `spacy_sentence` baseline for the sampled chunk settings: 114.715 ms average versus 146.544 ms.
4. `selectolax` is measured and shows synthetic selector-count parity with materially lower latency than BeautifulSoup: 25 ms average versus 664 ms.
5. No production replacement was promoted in this pass; promotion still requires real-source fixture parity and release artifact preservation checks.

## Verdict

- **Track 14 is complete enough to archive.**
- The implementation issue identified in the prior review, missing `orjson` and `selectolax` dependency-enabled reruns, has been addressed.
- The promotion gate closed conservatively: no serializer or tokenizer replacement was promoted; `selectolax` remains a documented future candidate for real-source adapter work.
- Remote push/full Actions verification remains environment-dependent, but Track 14 did not introduce a production replacement requiring release gating in this pass.

## Recommendation

Archive Track 14 after moving the final review and evidence with the track bundle.
