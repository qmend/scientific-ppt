$ErrorActionPreference = 'Stop'
$project = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
Push-Location $project
try {
    if (-not (Test-Path '.venv/Scripts/python.exe')) {
        python -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw 'Virtual environment creation failed' }
    }
    & .venv/Scripts/python -m pip install -r requirements.lock
    if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed' }
    & .venv/Scripts/python scripts/scientific_ppt.py doctor
    if ($LASTEXITCODE -ne 0) { throw 'Skill environment check failed' }
} finally { Pop-Location }
