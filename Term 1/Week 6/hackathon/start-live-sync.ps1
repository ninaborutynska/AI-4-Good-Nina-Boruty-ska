$ErrorActionPreference = 'Stop'
$sentimentRuntime = Join-Path $PSScriptRoot 'runtime/live'
New-Item -ItemType Directory -Path $sentimentRuntime -Force | Out-Null
$sentimentStatusPath = Join-Path $sentimentRuntime 'status.json'
if (Test-Path -LiteralPath $sentimentStatusPath) {
    $sentimentStatus = Get-Content -LiteralPath $sentimentStatusPath -Raw | ConvertFrom-Json
    $sentimentCheckedAt = if ($sentimentStatus.checked_at -is [DateTime]) {
        [DateTimeOffset]$sentimentStatus.checked_at
    } else {
        [DateTimeOffset]::Parse([string]$sentimentStatus.checked_at, [System.Globalization.CultureInfo]::InvariantCulture)
    }
    $sentimentPidPath = Join-Path $sentimentRuntime 'sync.pid'
    if ((Test-Path -LiteralPath $sentimentPidPath) -and (([DateTimeOffset]::UtcNow - $sentimentCheckedAt).TotalSeconds -lt 150)) {
        $sentimentSavedPid = [int](Get-Content -LiteralPath $sentimentPidPath)
        if (Get-Process -Id $sentimentSavedPid -ErrorAction SilentlyContinue) {
            Write-Output 'Live synchronization is already running.'
            exit 0
        }
    }
}
$sentimentPython = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
$sentimentSync = Start-Process -FilePath $sentimentPython -ArgumentList @('sync_github_live.py') -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $sentimentRuntime 'sync.stdout.log') -RedirectStandardError (Join-Path $sentimentRuntime 'sync.stderr.log') -PassThru
Set-Content -LiteralPath (Join-Path $sentimentRuntime 'sync.pid') -Value $sentimentSync.Id
Write-Output "Read-only live synchronization started (PID $($sentimentSync.Id)). Collector unchanged."
