# Cross-repository export packets

These files are issue/track proposals, not automatic code mutations. Review them against each repository's current branch and contracts before applying.

- `fyi-cli` uses `.conductor/`; add the live emitter track there and use its existing Project sync.
- The other listed repositories currently use `conductor/` conventions.
- Generic process-mining changes go to a Rust4PM fork/upstream PR only after the local direct-adapter test demonstrates the gap.
- Contract promotion removes the incubator copy from `foi-process` once the owning repository exposes a stable dependency.

Run `python scripts/export_dry_run.py` to print the proposed issue and Conductor destinations.
