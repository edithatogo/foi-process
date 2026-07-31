#!/usr/bin/env bash
set -euo pipefail
cargo fmt --all -- --check
cargo clippy --locked --all-targets --features rust4pm -- -D warnings
cargo test --locked --all-targets --features rust4pm
cargo doc --locked --no-deps --features rust4pm
cargo check --locked --all-targets --all-features
# DuckDB runtime tests require a separately provisioned native library. Match
# the hosted feature matrix here: compile all features, then execute the
# self-contained feature combinations. DuckDB has its own evidence workflow.
cargo test --locked --all-targets --features rust4pm,parquet,dataframes
cargo clippy --locked --all-targets --all-features -- -D warnings
cargo doc --locked --no-deps --all-features
rm -rf /tmp/foi-process-schemas
cargo run --locked --bin schema-gen -- /tmp/foi-process-schemas
python3 scripts/reference_pipeline.py
python3 scripts/validate_workpack.py
python3 scripts/test_reference_semantics.py
python3 scripts/validate_jurisdiction_profiles.py
PYTHONPATH=scripts python3 scripts/test_jurisdiction_profile_semantics.py
