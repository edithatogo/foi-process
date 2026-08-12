# Product Context

foi-process is a brownfield repository. Its README, released artifacts, and executable interfaces remain the product source of truth. Conductor records planned changes and evidence gates without changing those contracts.

The production source path is `fyi-cli` capture into a versioned `fyi-archive`
package, followed by `foi-process` validation and mining. `foi-process` may fetch
that pinned package from an approved archive mirror, including Hugging Face, but
must not independently discover or download source-site records. Raw archive
publication and derived process/dashboard publication are separate products.

