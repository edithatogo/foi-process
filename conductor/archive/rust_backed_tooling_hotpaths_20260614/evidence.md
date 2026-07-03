# Track 14 Evidence: Rust-Backed Tooling Hot-Path Experiments

## Acceptance Status

- **serializer_benchmark**: measured on 200 records / 8 iterations (`stdlib_json`, `msgspec_json`, and `orjson` measured)
- **parser_benchmark**: measured on synthetic fixture / 5 iterations (`beautifulsoup` and `selectolax` measured with selector-count parity)
- **tokenizers_benchmark**: measured on 120 records / 5 iterations (`tokenizers` measured, `spacy_sentence` measured)
- **adoption_decision**: **complete**, with no broad production replacement promoted from Track 14

## Repo-Side Artifacts

- `nlp-policy-nz/scripts/benchmark_msgspec_orjson.py`
- `nlp-policy-nz/scripts/benchmark_tokenizers_chunking.py`
- `corpus-cases-medilegal-nz/scripts/benchmark_selectolax_parser.py`
- `corpus-cases-medilegal-nz/tests/test_track14_selectolax_benchmark.py`
- `nlp-policy-nz/.tmp/track14_msgspec_orjson_benchmark.json`
- `nlp-policy-nz/.tmp/track14_tokenizers_chunking_benchmark.json`
- `corpus-cases-medilegal-nz/.tmp/track14_selectolax_parser_benchmark.json`
- `conductor/archive/rust_backed_tooling_hotpaths_20260614/evidence.md` (this file)
- `conductor/archive/rust_backed_tooling_hotpaths_20260614/review.md` (formal review)
- Local dependency overlay used for reruns: `.tmp/track14_libs` populated from wheels in `.tmp/track14_wheels`

## Latest Observed Results

- `track14_msgspec_orjson_benchmark.json`:
  - `stdlib_json` avg ≈ **2.346 ms**, throughput ≈ **64.10 MB/s**
  - `msgspec_json` avg ≈ **7.338 ms**, throughput ≈ **20.49 MB/s**
  - `orjson` avg ≈ **6.071 ms**, throughput ≈ **24.77 MB/s**
- `track14_tokenizers_chunking_benchmark.json`:
  - `tokenizers` avg ≈ **395.936 ms**, chunks `480`, throughput `1.66M chars/s`
  - `spacy_sentence` avg ≈ **287.262 ms**, chunks `6000`, throughput `2.29M chars/s`
- `track14_selectolax_parser_benchmark.json`:
  - `beautifulsoup` avg latency **3989 ms**, selector count `100000`
  - `selectolax` avg latency **304 ms**, selector count `100000`

## Notes

Dependency-enabled reruns were executed with:
- `benchmark_msgspec_orjson.py` using `PYTHONPATH=.tmp/track14_libs`
- `benchmark_selectolax_parser.py` using `PYTHONPATH=.tmp/track14_libs`

The scripts are still dependency-gated by design for environments without local wheels:
- if `orjson` is unavailable, status remains `missing_dependency`
- if `selectolax` is unavailable, status remains `missing_dependency`

Promotion decision:
- Do not replace current serializer paths with `msgspec_json` or `orjson` based on this fixture.
- Do not replace current chunking paths with Hugging Face `tokenizers` based on this sampled configuration.
- Treat `selectolax` as a validated candidate for a future real-source parser adapter change because it showed synthetic selector-count parity and materially lower latency; no production parser path was changed in Track 14.


