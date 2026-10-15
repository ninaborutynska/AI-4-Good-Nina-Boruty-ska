# Sentiment automation proposal

This is a proposal, not an enabled workflow. No collector, cron-job.org setting, or remote repository file has been changed.

## Access and required inspection

The GitHub connector currently cannot access `LuukAalders/Hackathons`. The collector's real workflow name, triggers, branch, permissions, commit/push steps, and recent run status are therefore unverified. Do not install the draft until those have been inspected.

## Proposed integration

1. Preserve the collector's existing cron-job.org trigger and all collector code.
2. Add a separate downstream `workflow_run` workflow, triggered only after a successful collector run. Set `workflows` to the exact inspected collector workflow name. Retain `workflow_dispatch` for a separate manual smoke test.
3. Validate with the artifact-only draft first. It has `contents: read` and cannot modify repository data. Stored repository predictions are inputs; new results are output artifacts. Artifact-only runs do not yet complete the automatic dashboard pipeline and will recompute uncommitted predictions on the next run.
4. After inspecting the collector's commit strategy and measuring runtime on actual comments, add publication of **only** `sentiment_results.csv` and `processing_status.csv`. Use one non-cancelling sentiment concurrency group, checkpoint results, reconcile onto the newest default-branch commit, and retry conflicts without force-pushing. Both writers must safely handle an intervening commit. If the collector cannot safely handle another writer, a writeback workflow is not safe during the monitoring period; use artifact validation until the collector write strategy can be reviewed with explicit permission.
5. Do not add a second collector schedule or change cron-job.org. An analysis failure must leave successful collection data intact. Add evaluation generation only after genuine manual annotations exist.

## Runtime and storage estimate

Executed locally on CPU: cached model smoke test took 24.04 seconds including imports/model load; inference for four padded test comments, including one long comment truncated to 512 tokens, took 4.622 seconds. These synthetic tests are **not** a representative throughput benchmark of the actual YouTube dataset. At that measured padded-batch throughput, 5,000 comments would take about 96 minutes for inference alone; a 45-minute runner timeout would be insufficient. Larger batches, realistic shorter comments, and GPU availability can change this substantially. Another isolated incremental test processed one short comment in 0.40 seconds including a warm model load. A GitHub runner benchmark is required before enabling automation. Set a per-run `--limit` if the backlog cannot fit the measured timeout; completed checkpoints must be published or carried forward before the next run.

### Updated estimate from actual comments

The supplied real CSV contains 2,486 comments. After an eight-comment smoke test, the main batch added 2,455 predictions in **177.63 seconds** on the local CPU with four threads and batches of 16. Rechecking language exclusions added 20 more in 6.01 seconds, for 2,483 classified comments total. A no-op incremental run took 0.08 seconds without loading the model. This real-data measurement is more informative than the padded synthetic estimate above. At the observed local rate, 5,000 similar comments would require about six minutes plus installation/model setup. A runner two to five times slower would require roughly 12–30 minutes (an estimate, not an executed runner test), fitting the proposed 45-minute timeout after cached setup in many cases. Benchmark a manually triggered artifact run before enabling writeback.

The source is 499,318 bytes and predictions are 423,695 bytes. They are far below GitHub's regular-file 100 MiB cap; the model cache must stay out of Git. [GitHub file limits](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github).

The Windows Hugging Face cache occupied about 1.00 GB because files were duplicated without symlinks. Linux cache behavior may use less storage. Cache the model revision with Actions cache; use short artifact retention. GitHub documents a six-hour hosted-job ceiling and a 10 GB cache allocation per repository; private-repository minutes and artifact allowances depend on the plan. The draft's 45-minute timeout is intentionally smaller than the platform ceiling. [GitHub Actions limits](https://docs.github.com/en/actions/reference/limits).

Automatic writes approximately every ten minutes could add up to 288 result commits in 48 hours; publish only when results change. At the current result size, repeatedly storing uncompressed full snapshots would be about 122 MB; Git history compression and growth from new comments change this estimate. Artifact validation without repository persistence will repeat the backlog, increasing runtime and billing; it is a short validation stage, not the final architecture. Account plan, available minutes, existing cache usage, permissions, and actual runner speed remain unverified.

## Approval boundary

The draft is intentionally outside `.github/workflows`. The task requires presenting potentially disruptive workflow changes before application. A complete writeback diff can only be proposed after inspecting the actual collector and proving the existing writer can coexist safely. No workflow publication or collector modification has been attempted.
