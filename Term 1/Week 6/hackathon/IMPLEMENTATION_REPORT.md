# Implementation report — 14 October 2026

**Live dashboard update:** `sync_github_live.py` now polls the private repository and completed analysis artifacts every 60 seconds, validates their provenance/integrity, and atomically publishes local snapshots for the app. The dashboard was rebuilt and its own port-3101 process restarted; the connected app showed 2,515 collected and 2,511 analysed comments, with evaluation ready and the actual monitoring timestamp. Three bridge tests and twelve dashboard tests passed, along with TypeScript and production build checks. No collector/workflow/cron-job.org/VideoLab changes were made for this connection. See `automation/LIVE_CONNECTION.md` for operation and credentials.

**Automation update:** repository access through the connected LuukAalders account is now working. A separate read-only artifact workflow and the required sentiment Python code were published in commit `3a4c83c308c0fb72e5aab18169550944ede19d78`. Collector workflow, collector source, cron-job.org triggers and VideoLab were preserved. The first hosted validation run is `38615905197`; see `automation/DEPLOYMENT_REPORT.md` for its verified outcome. Older access and automation limitations below describe the earlier implementation state.

The dashboard is running at **http://localhost:3101** with genuine local Hugging Face predictions. VideoLab responds at **http://localhost:3100**, retains its original process ID 26836, and was not modified or restarted.

## Real data and inference

- Source: `C:/Users/luuka/Downloads/youtube_comments.csv`, 2,486 unique comments. Its SHA-256 is unchanged: `376096e108d0541ae0f2e6365fa6287f382287846a3c5287add25232e81650c9`.
- Model: [cardiffnlp/twitter-roberta-base-sentiment-latest](https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest), exact revision `3216a57f2a0d9c45a2e6c20157c20c49fb4bf9c7`. Local Python, Transformers, PyTorch, Pandas; no training or external classification API.
- **2,483 successfully classified:** 302 Positive, 957 Neutral, 1,224 Negative. No inference failures.
- **3 unclassified:** one empty comment and two heuristically detected non-English comments. Status/reasons remain visible.
- Results: `C:/Users/luuka/Documents/New project/Hackathon 6/data/sentiment_results.csv`. All prediction IDs are unique, labels valid, and confidence scores between zero and one. Confidence is not verified accuracy.
- An initial eight-comment sample passed. The main run added 2,455 predictions in 177.63 seconds; the improved language check added 20 in 6.01 seconds. A complete incremental rerun processed zero new comments in 0.08 seconds without loading the model. Interruption recovery and new-ID processing also passed isolated correctness tests.

## Files created

All work is isolated under `C:/Users/luuka/Documents/New project/Hackathon 6`; existing application source and configuration were preserved.

| Area | Created files |
| --- | --- |
| Inference | `analyse_sentiment.py`, `sentiment/core.py`, `requirements-sentiment.txt`, isolated `.venv` and `.model-cache` |
| Local operation | `monitor_sentiment.py`, `download_data.py`, `start-dashboard.ps1`, `.gitignore`, runtime logs/PID |
| Predictions and validation | `data/sentiment_results.csv`, `data/processing_status.csv`, `data/verification_report.json`, `data/dashboard-preview.jpg` |
| Evaluation | `evaluate_sentiment.py`, `data/manual_labels.csv`, `data/evaluation.json` |
| Dashboard configuration | `dashboard/package.json`, lockfile, TypeScript configuration, Next environment declarations, environment template, ignored local environment configuration, Vitest configuration |
| Dashboard pages | `dashboard/app/layout.tsx`, `page.tsx`, `globals.css`, `evaluation/page.tsx`, `api/data/route.ts` |
| Dashboard logic | `dashboard/lib/data.ts`, `source.ts`, `components/Monitor.tsx`, `Evaluation.tsx`, `useData.ts` |
| Tests | Python pipeline/model/incremental tests and smoke reports; dashboard data and synchronization tests |
| Documentation and proposal | `README.md`, this report, `automation/PROPOSAL.md`, disabled `automation/sentiment-artifact.yml` |

## Dashboard connection and verification

The current server reads comments from the supplied Downloads folder and predictions/status/evaluation from `Hackathon 6/data`. It joins by comment ID and refreshes every 60 seconds with caching. Statistics, publication-time hourly/daily trends, doughnut distribution, searchable comment table, sentiment/date filters, confidence, and video links use real records. Selecting a chart point filters to the actual comments behind that bucket.

Private GitHub synchronization is implemented separately with a server-only environment token, commit-consistent reads, request coalescing, a 60-second cache, and stale/error states. It is **not configured** with a runtime token in this session. The connected GitHub installation belongs to another account and cannot access LuukAalders/Hackathons.

Executed checks: 10 Python tests, 11 TypeScript tests, type checking, production build, zero-known-advisory npm audit after dependency updates, genuine model smoke tests, source hash/CSV validation, both HTTP ports, real-data API counts, and browser behavior. An independent Pandas join confirmed the browser's 48 Negative Waymo comments for 1–14 October and one comment behind a selected hourly point. The evaluation page correctly shows no accuracy without human labels.

A hidden local watcher, PID 31464 at verification, checks the supplied CSV every 60 seconds and incrementally analyses changes. It does not download from GitHub; a fresh remote collection will only reach this watcher when the local file is updated. Runtime logs are in `runtime/`.

## Remaining configuration and human work

1. Configure read-only GitHub server credentials for automatic remote data loading, and access to the actual collector workflow for inspection.
2. Review the downstream workflow proposal, run artifact-only inference on a GitHub runner, then approve/install safe result publication after checking the collector's Git commit strategy. The draft is outside `.github/workflows` and has not been enabled. Local real-data runtime is about three minutes for the backlog; hosted-runner speed and account quotas remain unverified.
3. Supply `monitoring_started.txt` and `collection_log.csv`. The actual 48-hour start is currently unavailable, so publication periods are Unknown. Last collection is calculated from the real comments.
4. **Completed on 14 October 2026:** 60 genuine human annotations were imported, including two explicit chat completions. Nine off-topic comments are excluded; the comparison uses 51 relevant comments. RoBERTa matches 32/51 (62.7%) and VADER 17/51 (33.3%). Both confusion matrices and three supplied human failure explanations are available. See `EVALUATION_REPORT.md`; this sample accuracy is not verified population-level accuracy.

The original YouTube CSV was not overwritten. No remote collector file, log, GitHub workflow, cron-job.org setting, VideoLab dependency, environment variable, database, or configuration was changed. Current remote collector Actions health remains unverified because repository access is unavailable.
