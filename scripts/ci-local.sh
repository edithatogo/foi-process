#!/usr/bin/env bash
set -euo pipefail
cargo fmt --all -- --check
cargo clippy --locked --all-targets --features rust4pm -- -D warnings
cargo test --locked --all-targets --features rust4pm
cargo doc --locked --no-deps --features rust4pm
cargo check --locked --all-targets --all-features
cargo test --locked --all-targets --all-features
cargo clippy --locked --all-targets --all-features -- -D warnings
cargo doc --locked --no-deps --all-features
rm -rf /tmp/foi-process-schemas
cargo run --locked --bin schema-gen -- /tmp/foi-process-schemas
python3 scripts/reference_pipeline.py
python3 scripts/validate_workpack.py
python3 scripts/test_reference_semantics.py
