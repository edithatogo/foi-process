$ErrorActionPreference = 'Stop'

$required = @(
  'README.md', 'Cargo.toml', 'renovate.json', 'CONTRIBUTING.md', 'SECURITY.md',
  '.github/pull_request_template.md', 'conductor/index.md', 'conductor/product.md',
  'conductor/product-guidelines.md', 'conductor/tech-stack.md', 'conductor/workflow.md',
  'conductor/tracks.yaml', 'conductor/tracks.md'
)

foreach ($path in $required) {
  if (-not (Test-Path -LiteralPath $path)) { throw "Missing required repository context: $path" }
}

if (Test-Path -LiteralPath '.github/dependabot.yml') {
  throw 'Dependabot configuration remains present; use Renovate as the sole update system.'
}

Write-Output "Repository context valid: $($required.Count) required paths checked; Renovate-only dependency policy confirmed."
