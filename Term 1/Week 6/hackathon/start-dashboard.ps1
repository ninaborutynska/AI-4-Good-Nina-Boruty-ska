$ErrorActionPreference = 'Stop'
$dashboardDirectory = Join-Path $PSScriptRoot 'dashboard'
if (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'runtime/live/github-token')) {
    & (Join-Path $PSScriptRoot 'start-live-sync.ps1')
}
$existingListener = Get-NetTCPConnection -LocalPort 3101 -State Listen -ErrorAction SilentlyContinue
if ($existingListener) {
    Write-Output 'Port 3101 is already in use. No existing process was stopped or restarted.'
    exit 0
}
if (!(Test-Path -LiteralPath (Join-Path $dashboardDirectory '.next/BUILD_ID'))) {
    throw 'Build the sentiment dashboard first with npm.cmd run build in its dashboard folder.'
}
$nodeExecutable = (Get-Command node.exe).Source
$runtimeDirectory = Join-Path $PSScriptRoot 'runtime'
New-Item -ItemType Directory -Path $runtimeDirectory -Force | Out-Null
$sentimentServer = Start-Process -FilePath $nodeExecutable -ArgumentList @('node_modules/next/dist/bin/next', 'start', '--hostname', '127.0.0.1', '--port', '3101') -WorkingDirectory $dashboardDirectory -WindowStyle Hidden -RedirectStandardOutput (Join-Path $runtimeDirectory 'dashboard.stdout.log') -RedirectStandardError (Join-Path $runtimeDirectory 'dashboard.stderr.log') -PassThru
Write-Output "Sentiment dashboard started with process ID $($sentimentServer.Id). Open http://localhost:3101."
