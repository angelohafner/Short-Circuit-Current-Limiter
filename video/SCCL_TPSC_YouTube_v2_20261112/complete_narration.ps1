$ErrorActionPreference = 'Stop'
$revisionRoot = $PSScriptRoot
Push-Location -LiteralPath $revisionRoot
try {
    # Run in a normal local terminal with network access. This script does not
    # change proxy, security, execution-policy, registry, or machine settings.
    & py -3.11 -m pip install --disable-pip-version-check --target (Join-Path $revisionRoot 'dependencies/tts') 'edge-tts==7.3.1'
    if ($LASTEXITCODE -ne 0) { throw 'Narration dependency installation failed.' }
    & py -3.11 (Join-Path $revisionRoot 'generate_narration.py') --engine edge
    if ($LASTEXITCODE -ne 0) { throw 'Narration generation failed; see evidence/narration_attempt.json.' }
    & py -3.11 (Join-Path $revisionRoot 'validate_narration.py')
    if ($LASTEXITCODE -ne 0) { throw 'Narrated video validation failed.' }
} finally {
    Pop-Location
}
