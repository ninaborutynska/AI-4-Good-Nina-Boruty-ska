# Live dashboard connection — 14 October 2026

Dashboard: http://localhost:3101

Local connection management: http://localhost:3101/connection

## Data flow

cron-job.org / existing GitHub schedule → unchanged collector → private GitHub CSV → separate existing sentiment workflow → analysis artifact → read-only local bridge → dashboard.

`sync_github_live.py` runs hidden on this computer, checks GitHub every 60 seconds, and reads current `main` plus the latest successful `sentiment.yml` run's artifact. It never invokes, cancels or alters collection, never pushes files, and needs only Contents: Read and Actions: Read. GitHub cloud collection and analysis continue independently when this computer or app is off.

Comments/logs/monitoring-start are read from a single source commit. Predictions/status/report come from a completed trusted main-branch analysis run. The artifact ZIP digest, source SHA-256 at the analysed commit, record counts, comment IDs, confidence bounds, labels, source preservation and zero recorded inference failures are checked before use. Newer collected comments can be shown as pending while cloud analysis catches up. No dummy data is introduced.

The bridge writes complete immutable generations under `runtime/live/snapshots/`, then atomically switches `runtime/live/current.json`. A failed refresh retains the last complete generation. The dashboard reads this manifest using `LIVE_SYNC_DIR=../runtime/live`, refreshes every 60 seconds, and warns if the bridge reports failure or has not checked in for three minutes. Normal end-to-end delay includes the existing collector cadence, cloud analysis time (first measured run: about six minutes), bridge polling and browser refresh. It is periodically refreshed live data, not a per-second stream.

Genuine local manual labels are preserved and their evaluation is regenerated against the downloaded predictions. The original Downloads CSV, local prediction files, and all human annotations remain unmodified.

## Credentials

**15 October fix:** Connection now distinguishes saved credentials, temporary sync failure, automatic restart and an explicitly rejected token. A saved key is no longer presented as missing on transient failures. The credential form is hidden until replacement is requested, and the app automatically restarts a stale bridge using the saved credential. Python's existing file lock prevents simultaneous writers. Fifteen dashboard tests, TypeScript and the production build passed, including saved-key persistence during transient failure, throttled restart and secret exclusion checks.

The runtime token is stored only in ignored `runtime/live/github-token`; it is never committed, sent in browser API responses or written to logs. The Connection page permits same-origin loopback-only replacement, checks both required read permissions first, and clears the input on successful save. It never returns the saved token. A token that was pasted in chat should be replaced/revoked through GitHub; enter its replacement only in this local page. The bridge rereads credentials each cycle.

An existing external token file is also supported with `GITHUB_TOKEN_FILE`, or ignored `runtime/live/credentials.json` containing `token_file`. A plain token or `GITHUB_TOKEN=...`/`GH_TOKEN=...` dotenv entry is accepted. Do not publish credentials or token file contents.

## Start and recovery

Run `start-dashboard.ps1` from this project to start the dashboard and, when the local token exists, its hidden sync process. `start-live-sync.ps1` starts only the bridge and avoids starting another recent active instance. Runtime PID, status and sanitized logs live in `runtime/live/`. `sync_github_live.py --once` performs one complete read-only cycle for diagnosis. The live bridge must have ordinary outbound HTTPS access to api.github.com and GitHub artifact storage.

The current app is bound to loopback port 3101. Only the verified sentiment process on that port was restarted for this change. VideoLab was neither inspected nor stopped. No Windows login task or system-wide setting was installed; after reboot, start this project's launcher again. Collection in GitHub remains independent.

## Verification

- Three isolated bridge tests passed: newer comments with older valid predictions, keeping the published snapshot on interrupted download, and rejecting a corrupted artifact.
- Twelve dashboard tests passed, including atomic-generation reading and stale bridge detection; TypeScript checking and production build passed.
- Real read-only sync succeeded, then a later background cycle advanced the source commit automatically.
- The real app API returned `Live GitHub synchronization`, 2,515 collected, 2,511 analysed, evaluation ready, and monitoring start `2026-10-13T07:50:17.678Z` at initial verification.
- Browser verification showed the same real counts, GitHub sync timestamp, monitoring window, and Connection page connected state with an empty credential input.
- The original collector, its GitHub workflow, cron-job.org configuration, and VideoLab were unchanged throughout this integration.

Snapshots are retained locally for recovery and are not a replacement for the repository dataset. Artifact retention remains three days; if the cloud analysis stops longer than that, the bridge will retain its last snapshot and report the problem.
