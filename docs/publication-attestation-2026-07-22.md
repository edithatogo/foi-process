# Publication attestation - 2026-07-22

The reviewed synthetic/public-safe event-log bundle was published to
`edithatogo/foi-process-event-logs` at revision
`3977b10d8ae87a2a16ad0991d4bc9718b81ee293`.

- Manifest files: 38
- Manifest SHA-256: `5150fcaf43627bf7d4020e65f59c845eb6f5256b7d6ddd7329930f30144db4b6`
- GitHub Pages deployment: workflow `29892354639`
- Dashboard: https://edithatogo.github.io/foi-process/

The former `edithatogo/foi-process-explorer` Space was removed after its
runtime reported `CONFIG_ERROR`. The surviving free Space is
`edithatogo/foi-process-explorer-free`. A later upload attempt returned HTTP
402 while trying to create the Space, so the already-running free Space was
preserved. No paid hardware or service was enabled.

The first publication workflow verification failed because its environment
omitted the `click` dependency required by the Hugging Face CLI; the dataset
was subsequently uploaded and independently verified against the remote
manifest.
