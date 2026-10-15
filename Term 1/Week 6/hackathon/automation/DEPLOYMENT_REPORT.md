# Sentiment artifact validation — 14 October 2026

Published commit: https://github.com/LuukAalders/Hackathons/commit/3a4c83c308c0fb72e5aab18169550944ede19d78

First hosted run: https://github.com/LuukAalders/Hackathons/actions/runs/38615905197

The user reviewed the integration proposal and authorized continuation. The installed workflow is `.github/workflows/sentiment.yml`; its local source is `automation/sentiment.yml`. Six supporting Python/dependency/test files were published alongside it. No existing remote files were changed by this commit. In particular, `.github/workflows/collect.yml`, `collect_comments.py`, the collector dataset, and all existing triggers were preserved. No VideoLab files, processes or configuration were accessed or changed.

## Behavior

- Read-only repository access; checkout credentials are not persisted.
- Runs after successful `YouTube Comment Collector` completion on `main`, only for this repository. Manual dispatch is available. A push affecting the sentiment workflow itself starts bootstrap validation without another collector invocation.
- Python 3.12 on Ubuntu, CPU inference, exact model revision, pip/model caches, one sentiment run at a time, 45-minute timeout.
- Outputs go to the runner temporary directory, never the original dataset. Prediction/status CSVs and a report are retained as an artifact for three days, including available checkpoints on failure.
- The report records the input commit, source SHA-256, processing counts and source preservation. Inference failures or missing input IDs fail validation.
- No automatic result commit, artifact reuse, manual-label publication or local dashboard reconfiguration. Full real-source inference is repeated per validation run; this is an initial validation stage, not the final incremental publication design.

## Verification

- All 11 existing pipeline tests passed locally. Windows sandbox temporary-file creation required setting TEMP/TMP to a project-local test directory for that command only; no global environment was changed. The two earlier stuck test processes were interrupted through their own command sessions.
- The new CI wrapper passed a local resume/no-op check on the real dataset using copies of existing predictions/statuses in `runtime/ci-validation`. It retained 2,483 predictions and 2,486 statuses, with zero new failures and unchanged source SHA-256 `376096e108d0541ae0f2e6365fa6287f382287846a3c5287add25232e81650c9`.
- The remote commit adds exactly seven files and deletes none. A collector commit arrived during preparation; publication was rebuilt on its latest head with a normal guarded ref update, preserving that data.
- First hosted run completed successfully. Hosted inference took 345.63 seconds (5 minutes 46 seconds); the entire job including cold installation, model download, artifact upload and cache saves took about 7 minutes. All 11 runner pipeline tests passed. The real GitHub source contained 2,514 comments: 2,511 classified, 3 skipped, zero inference failures, zero duplicate IDs or missing IDs. Source SHA-256 remained `7b1ba40406a924f09eb7d134839b6c3343b21f5d85c68a66ff82b60fd0b2bfcf`. See `hosted-validation.json` for the structured log report.
- Artifact `sentiment-checkpoints-38615905197-1` was uploaded successfully (207,445 bytes), expires on 17 October 2026, and has SHA-256 `4f5e7a9959114eba50f4cd1aa314f5834b530f34be47fa8324c7ca3a0bcbc65d`. Download: https://github.com/LuukAalders/Hackathons/actions/runs/38615905197/artifacts/11920815729 . Metadata and the successful upload were checked; artifact CSVs have not been separately downloaded and re-audited.
- Both pip and model caches were saved. This measured run fits the ten-minute cadence, but repeated full-dataset analysis is deliberately limited to this initial artifact validation architecture; growing data can extend runtime. Account minute/storage allowances remain unverified.

## Next publication stage

After hosted validation, result publication needs a separate tested change: persist only the two sentiment CSVs, restore completed IDs for incremental analysis, rebase/retry ordinary pushes without force, and verify coexistence with the collector's one-shot push. The dashboard additionally needs its own read-only runtime GitHub credentials or another explicit source synchronization mechanism.
