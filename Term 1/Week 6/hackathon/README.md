# Autonomous Driving Sentiment Monitor

**Authors:** Luuk and Nina

An English-language research dashboard that collects YouTube comments about self-driving cars, classifies their sentiment and lets users inspect the comments behind the statistics.

**Research question:** How does public sentiment toward self-driving cars change over time, based on YouTube comments?

The project combines automated data collection, a pretrained language model, human evaluation and interactive visualisation. It relates to **SDG 9: Industry, Innovation and Infrastructure**, through its focus on autonomous mobility and public discussion of technological innovation. The findings describe the selected YouTube discussions, rather than the views of the entire population.

## The problem

Self-driving cars are moving from tests to public roads, and cities have to decide whether to let them in. Public opinion is divided:

- In a poll of 8,418 adults in nine European capitals (OpinionWay for Clean Cities, fieldwork November 2025), 37% supported the arrival of autonomous vehicles, 35% opposed it and 28% were undecided.
- In the United States, 6 in 10 drivers say they are afraid to ride in a self-driving vehicle, and 53% would not choose to ride in a robotaxi (AAA survey, January 2025).
- Resistance can turn physical: in February 2024 a crowd in San Francisco vandalised a Waymo robotaxi and set it on fire.
- The technology is arriving in Europe: on 10 April 2026 the Dutch vehicle authority RDW approved Tesla's FSD Supervised, a driver assistance system in which the driver stays responsible.

Surveys like these are done once or twice a year. Between them, people write every day what they think, but nobody can read all of it, so a city often notices a change in mood only when an incident is already in the news.

Sources: Clean Cities (27 January 2026) https://cleancitiescampaign.org/?p=26039 · AAA (25 February 2025) https://southjersey.aaa.com/news/aaa-fear-self-driving-vehicles-persists · TechCrunch (12 February 2024) https://techcrunch.com/2024/02/12/a-waymo-robotaxi-was-vandalized-and-burned-in-san-francisco · The Next Web (12 April 2026) https://thenextweb.com/news/tesla-fsd-supervised-netherlands-europe

## Named user and decision

**User:** a transport-policy analyst at a city council.

**Decision:** whether to support a pilot with self-driving taxis or shuttles in the city, and which public concerns (safety, damage to vehicles, trust in the technology) to address in the communication before it starts.

**How they use the dashboard:** they follow the daily trend, open the comments behind a negative dip to see what caused it, and treat this as a signal next to surveys and consultation, not as a replacement for them.

**Who is missing from the stream:** people who do not comment online, older people, people who write in other languages, and most residents of the analyst's own city.

## User group and purpose

The intended users are mobility researchers, transport-policy analysts and organisations developing autonomous transport. They need to explore reactions to autonomous driving, identify changes in online discussion and read the evidence behind positive or negative sentiment. Reviewing thousands of comments manually makes this difficult to do consistently.

The dashboard supports this exploratory work with sentiment trends, date filters, a searchable comment table and links to the source videos. For example, a researcher can select a negative trend and inspect whether the underlying comments concern vehicle behaviour, sarcasm or an unrelated argument.

YouTube commenters provide the source material; they are not necessarily users of the dashboard. Drivers and passengers may benefit indirectly from better-informed research, but the application does not provide personal travel advice or assess vehicle safety. This is an intended user group, not a claim that stakeholder interviews, usability testing or deployment with these organisations have already taken place.

Innovation in transport involves both technical development and questions about public trust. Exploring these discussions is relevant to [SDG 9](https://sdgs.un.org/goals/goal9). Sentiment data alone cannot demonstrate that autonomous transport improves safety, sustainability or infrastructure.

### The problem in practice and why this approach fits

A transport-policy analyst reviewing discussion around autonomous driving needs to distinguish reactions to the technology from the emotional tone of a sentence. In the manually labelled sample, a comment approving damage to a vehicle was classified as Positive even though the human annotator judged its attitude toward autonomous driving to be Negative. This observed error shows why an aggregate chart needs links back to the underlying comments. It is evidence of a problem in interpreting this dataset, rather than evidence from stakeholder interviews.

The concrete SDG 9 issue addressed is the difficulty of examining concerns about an emerging transport technology in a traceable way. Researchers and transport analysts can use the dashboard to locate discussion requiring closer investigation. This supports exploratory research into innovation; it does not demonstrate increased public acceptance or improved infrastructure.

Manual reading provides context, but repeatedly reviewing the accumulated dataset is laborious. Keyword counts cannot reliably distinguish praise, criticism and sarcasm in context. RoBERTa provides repeatable initial classification, while date filters and source-comment inspection help users question its output. The comparison with VADER tests a simpler alternative: RoBERTa matched more human labels on the evaluated sample, although its remaining errors mean that human review is still necessary. No stakeholder time savings have been measured.

## How the data was collected

The source material is public comments on YouTube videos about autonomous driving. Video IDs are recorded in [`video_ids.csv`](https://github.com/LuukAalders/Hackathons/blob/main/Hackathon%206/video_ids.csv). The collector uses the **first 20 unique video IDs** from that file. This is a fixed, topic-focused sample rather than a random sample of YouTube. The saved list makes the selected IDs traceable, but does not contain a complete search-query or ranking history.

Comments are retrieved using Python and the official [YouTube Data API v3 `commentThreads.list` endpoint](https://developers.google.com/youtube/v3/docs/commentThreads/list). Requests use `order=time`, `textFormat=plainText` and up to 100 comment threads per page. For each video, the script checks up to three pages and stores the top-level comment from each returned thread. Replies are not included. This retrieves recent available comments, including comments that already existed when collection began; it does not guarantee complete historical coverage.

The collector runs in GitHub Actions. cron-job.org triggers it approximately every ten minutes; the existing workflow also has a ten-minute GitHub schedule and supports manual dispatch. Execution times can vary, so actual checks are recorded in the collection log. The cloud collector continues independently of the local dashboard.

Each run loads the existing CSV and compares returned `comment_id` values with previously stored IDs. Only unknown IDs are appended. A final deduplication step ensures that repeated checks do not count the same comment twice. Previously stored text is retained, so later edits or deletions on YouTube are not automatically reflected. Individual video failures are logged; the run fails if every video request fails.

The dataset contains these fields:

| Field | Description |
| --- | --- |
| `comment_id` | Unique comment identifier used for deduplication and joining predictions |
| `video_id` | Source video identifier |
| `text` | Comment text returned by the API |
| `published_at` | Publication timestamp on YouTube |
| `collected_at` | Timestamp when the collector first stored the comment |

Publication and collection timestamps serve different purposes: the dashboard uses publication time for sentiment trends, while collection time shows when data entered the system. The collection log records check times, successful/failed videos, new comments and total comments.

### Terms of the stream

The YouTube Data API v3 needs a free API key from Google Cloud and allows 10,000 units per day. We use the official API and do not scrape the website, which the YouTube API Services Developer Policies do not allow. The same policies say that data fetched without user authorisation may be stored for no longer than 30 calendar days and must then be deleted or refreshed, so this dataset is a snapshot for a course prototype and must not be kept or reused beyond that. Policy page: https://developers.google.com/youtube/terms/developer-policies

## System architecture

```text
Selected YouTube videos
        ↓
YouTube Data API
        ↓
Python collector in GitHub Actions
        ↓
Original comment CSV and collection log
        ↓
Separate Python sentiment analysis workflow
        ↓
Validated prediction artifact
        ↓
Read-only local GitHub synchronization
        ↓
Next.js dashboard and interactive charts
```

The collector and sentiment workflow run separately. A failed analysis does not undo collected data. After successful collection, the sentiment workflow analyses the dataset and uploads predictions, processing statuses and a validation report as a GitHub Actions artifact. It has read-only repository access and does not commit predictions back to the collector's branch. Artifacts are retained for three days.

The local synchronization process checks GitHub every 60 seconds. It retrieves the current collector data and the latest successful sentiment artifact, verifies the artifact digest and analysed source hash, and validates record counts, IDs, labels and confidence values. Only a complete snapshot becomes visible to the dashboard. Comments and predictions are joined using `comment_id`.

The browser refreshes every 60 seconds. Newly collected comments can appear as awaiting analysis until the cloud workflow finishes. If synchronization fails, the last complete snapshot remains visible with a warning. The app reuses its stored credential and can restart a stale synchronization process automatically. The local dashboard needs the computer to be running; GitHub collection and analysis operate independently.

## Sentiment model

The classifier is [`cardiffnlp/twitter-roberta-base-sentiment-latest`](https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest), a pretrained English RoBERTa model. Its social-media training domain makes it a plausible starting point for informal comments, although performance on YouTube and attitudes toward autonomous driving still requires evaluation.

The model runs through **Python, Hugging Face Transformers and PyTorch**. It is not trained or fine-tuned for this project. Comments are not submitted to a generative AI classification API. Inference runs in Python, locally or on a GitHub runner; the browser only displays saved predictions.

The model revision is pinned for reproducibility:

```text
3216a57f2a0d9c45a2e6c20157c20c49fb4bf9c7
```

Usernames and links are normalised following the model's preprocessing approach. Comments are tokenised and truncated to at most 512 tokens. The output is **Positive**, **Neutral** or **Negative**, with the selected label's softmax probability. Confidence represents the model's preference between labels; it is not measured accuracy.

The local analysis script processes pending IDs in batches, saves checkpoints and skips completed predictions on subsequent runs. A file lock prevents simultaneous writers. A failed batch is split to isolate individual errors. The hosted artifact workflow currently performs a fresh analysis each run: it caches model weights, but does not restore earlier prediction artifacts for incremental processing. The first verified hosted run classified 2,511 comments in approximately 5 minutes 46 seconds.

Empty comments, malformed records, confidently detected non-English text and inference failures receive explicit statuses. Short text, uncertain language, possible spam, low confidence and truncation can carry quality flags. Language detection is heuristic. The pipeline does not establish that every comment is relevant to autonomous driving.

Prediction output fields are `comment_id`, `sentiment`, `confidence`, `model_version` and `analysed_at`. Processing statuses are stored separately. Inference does not overwrite the original comments or collection log.

**Model card summary:** trained on about 124 million tweets from January 2018 to December 2021 and fine-tuned for sentiment on the TweetEval benchmark. English only. Labels: Negative, Neutral, Positive. Licence: CC BY 4.0. We chose it because tweets are short and informal like YouTube comments.

## Dashboard features

The dashboard runs at **[http://localhost:3101](http://localhost:3101)** and includes:

- Total collected, analysed and pending comments; sentiment percentages; and an overall score.
- Hourly or daily sentiment trends, date filters and selectable chart points for inspecting the underlying comments.
- A sentiment-distribution chart that follows the active filters.
- A searchable comment table with text, publication/collection timestamps, sentiment, confidence, quality flags and video links.
- Latest synchronization, collection and analysis timestamps, plus connection warnings.
- A separate [model evaluation page](http://localhost:3101/evaluation).

Percentages use successfully classified comments only. Pending totals include unprocessed and skipped/failed comments, with the latter subtotal shown separately. All chart dates use UTC. Lines connect observed time buckets and do not imply measured values between them.

The overall sentiment score is:

```text
100 × (positive comments − negative comments) / analysed comments
```

It ranges from −100 to +100. This is a descriptive index rather than a validated measure of public acceptance.

## Dataset and observed results

The verified snapshot on **15 October 2026 at 10:51 UTC** contains **2,533 unique comments**, including comments already available when collection began. The live dashboard can show newer data. The source is recorded in [GitHub commit `56fa311d1543`](https://github.com/LuukAalders/Hackathons/tree/56fa311d1543ba31f091b344822ce73a30160375/Hackathon%206/data).

| Result | Count |
| --- | ---: |
| Unique comments collected | 2,533 |
| Successfully classified comments | 2,530 |
| Positive predictions | 306 |
| Neutral predictions | 975 |
| Negative predictions | 1,249 |
| Empty comments | 1 |
| Detected non-English comments | 2 |

The selected video list contains more IDs than the collector uses. Twenty videos were checked in the initial and latest logged runs; 19 contributed stored comments to this snapshot.

Negative predictions form the largest category in the accumulated dataset. This makes critical discussion a useful focus for inspection, but does not establish that most people oppose autonomous driving. The comments include differing publication dates, multiple comments can come from the same person, and the videos and commenters are self-selected. Changes in chart percentages are exploratory observations; they cannot by themselves demonstrate a change in population opinion or a causal effect of a news event.

## Human evaluation and comparison

A sample of **60 real comments** was manually labelled for attitudes toward autonomous driving. Nine were judged not relevant and excluded from the sentiment comparison. The remaining **51 relevant comments** contain 26 Negative, 17 Neutral and 8 Positive human labels. Human annotations are stored separately from predictions.

RoBERTa was compared with **VADER 3.3.2**, a lexicon-based baseline. VADER uses compound thresholds of +0.05 for Positive and −0.05 for Negative, with intermediate values classified as Neutral. Both models were compared against the same matched human labels.

| Model | Matches with human labels | Sample accuracy |
| --- | ---: | ---: |
| RoBERTa | 32 / 51 | 62.7% |
| VADER | 17 / 51 | 33.3% |

RoBERTa performed better on this sample, but disagreed with the annotator on 19 comments. This small, single-annotator sample does not establish accuracy on all comments or agreement between different annotators. General textual sentiment and an attitude toward a specific technology can also differ.

Three observed RoBERTa errors illustrate these issues:

| Comment excerpt | Human label | Model label | Explanation |
| --- | --- | --- | --- |
| “😂😂😂 Technology gonna save us!!” | Neutral | Positive | The annotator interpreted the statement as sarcasm rather than literal praise. |
| “C'mon guys you could've hit it with your high intensity water hose.” | Negative | Positive | Approval of damaging the vehicle does not express support for autonomous driving. |
| “Talk about a ‘smart’ car... 😂😂” | Negative | Positive | “Smart” is used to mock the vehicle's behaviour. |

Both confusion matrices and the complete explanations are included in [EVALUATION_REPORT.md](EVALUATION_REPORT.md). The dashboard checks evaluation-file hashes to avoid displaying an outdated comparison as current.

## Limitations and responsible use

The fixed video selection and self-selected commenters introduce bias. The project measures discussion in the sampled comments, not representative public opinion. The collector retrieves top-level comments only, checks a limited number of pages and retains the first stored version of a comment. Some comments can therefore be missed or become outdated.

The English model can misinterpret sarcasm, emojis, slang, mixed opinions and mixed-language text. Language detection can wrongly include or exclude comments, and truncation can omit context. Promotional posts and off-topic arguments may remain in the dataset. Users should inspect comments behind a trend before interpreting it as support for or opposition to autonomous driving.

The collector stores only the five documented fields, without author profile fields. However, comment text and traceable comment IDs can still expose personal information, so the dataset is not fully anonymous. The collector's own repository is private. This portfolio copy is public so that it can be graded, and the comment data should be removed from it after grading, in line with YouTube's 30-day storage limit. Report examples should be limited to necessary excerpts and avoid personal details. The dashboard should not be used to profile individuals or make vehicle-safety decisions.

Model caching reduces repeated downloads, but full hosted reanalysis still consumes computing resources. Future improvements include restoring validated predictions for incremental cloud inference, documenting video-selection queries, collecting broader samples, using independent annotators and adding target-specific relevance classification. No improvement in public trust, safety or SDG outcomes has been measured.

## Ethical reflection

| Risk specific to this prototype | Possible consequence | Current safeguard and remaining action |
| --- | --- | --- |
| Public comment text and IDs remain traceable | Republishing examples could expose commenters to unwanted attention or reveal personal details. | Author-profile fields are not collected. The collector's repository is private; this public portfolio copy is for grading, and the comment data should be removed after grading. Use only necessary excerpts and inspect them for personal information before sharing. These measures do not make the data anonymous. |
| Fixed videos, self-selected commenters and an English model exclude other voices | Researchers or policy analysts could overestimate opposition or mistake a selected discussion for population opinion. | The sampling method and limits are disclosed, and conclusions are restricted to the sampled comments. Broader sampling is a proposed next step. |
| Sarcasm and target-specific attitudes can be misclassified | Users could interpret criticism as support and draw misleading conclusions about autonomous mobility. | Users can inspect source comments, quality flags and the human-label comparison. Independent annotation and relevance classification remain proposed improvements. |
| Hosted analysis repeats full inference | Reprocessing unchanged comments consumes additional computing resources without adding new predictions for those comments. | Model weights are cached to reduce downloads. Restoring validated predictions for incremental cloud inference is a proposed improvement; energy savings have not been measured. |

The intended users remain responsible for interpreting results. The dashboard should not be used to profile commenters, establish vehicle safety or represent public consensus.

## Demonstrate the prototype

After starting the app using the instructions below:

1. Open the dashboard and show the collected, analysed and pending totals and the latest synchronization status.
2. Select an hourly or daily view and a date range. Select a chart point to inspect the comments behind the displayed sentiment.
3. Search the comment table, inspect a label and its confidence, and follow a source-video link. Explain that confidence is not measured accuracy.
4. Open `/evaluation` and compare RoBERTa with VADER against the human annotations. Use one documented error to show why human interpretation remains necessary.
5. Explain the separate collection, analysis and synchronization processes. A dashboard refresh checks for completed data; it does not itself initiate collection or guarantee a new comment.

The presentation is available in [PowerPoint format](outputs/presentation/Autonomous_Driving_Sentiment_Monitor_v3.pptx). A short screen recording of the dashboard is in [demo_video.mp4](demo_video.mp4).

## Run the application

Requirements: Python 3.12 or a compatible supported version, Node.js 22 or newer, npm and network access for initial downloads. Run these commands from the `Hackathon 6` directory, preserving any existing environment or credential files.

```powershell
if (!(Test-Path .venv)) { python -m venv .venv }
& '.\.venv\Scripts\python.exe' -m pip install -r requirements-sentiment.txt requests

cd dashboard
npm.cmd ci
if (!(Test-Path .env.local)) { Copy-Item .env.example .env.local }
```

For live GitHub synchronization, set these non-secret values in `dashboard/.env.local`:

```dotenv
DATA_SOURCE=local
LIVE_SYNC_DIR=../runtime/live
LOCAL_DATA_DIR=../data
LOCAL_RESULTS_DIR=../data
```

Build and start:

```powershell
# From Hackathon 6/dashboard
npm.cmd run build
cd ..
& '.\start-dashboard.ps1'
```

Open [Connection](http://localhost:3101/connection) and save a fine-grained GitHub token restricted to `LuukAalders/Hackathons`, with **Contents: Read** and **Actions: Read**. It is stored in the ignored local runtime directory and never included in dashboard responses. A valid saved key does not need to be re-entered after reopening the app.

The collector uses a separate `YOUTUBE_API_KEY` secret in GitHub Actions. The dashboard credential provides read access and does not start collection or grant repository write access. Keep tokens and `.env` files out of version control. After a computer restart, run `start-dashboard.ps1` again. The first synchronization may take longer than a regular refresh.

### Local analysis and offline use

For local CSV use, leave `LIVE_SYNC_DIR` empty and configure `LOCAL_DATA_DIR` with the collected files and `LOCAL_RESULTS_DIR` with predictions and evaluation files. Inference without internet requires the model to be cached already.

From `Hackathon 6`, analyse a real local dataset with:

```powershell
& '.\.venv\Scripts\python.exe' analyse_sentiment.py `
  --input 'C:\path\to\youtube_comments.csv' `
  --revision 3216a57f2a0d9c45a2e6c20157c20c49fb4bf9c7 `
  --device cpu
```

The default outputs are `data/sentiment_results.csv` and `data/processing_status.csv`. To refresh the human-label comparison, run `evaluate_sentiment.py --comments 'C:\path\to\youtube_comments.csv'`; genuine annotations are read from `data/manual_labels.csv`.

## Project files and verification

| Component | Files |
| --- | --- |
| Collection in the GitHub repository | `collect_comments.py`, `video_ids.csv`, `.github/workflows/collect.yml` |
| Sentiment inference | `analyse_sentiment.py`, `sentiment/core.py`, `requirements-sentiment.txt` |
| Human evaluation | `evaluate_sentiment.py`, `data/manual_labels.csv`, `EVALUATION_REPORT.md` |
| Hosted analysis | `.github/workflows/sentiment.yml`; local source in `automation/sentiment.yml` |
| Local synchronization | `sync_github_live.py`, `start-live-sync.ps1` |
| Dashboard | `dashboard/`, `start-dashboard.ps1` |
| Technical tests | `tests/`, `dashboard/tests/` |

Executed checks cover real-model inference, source preservation, incremental processing, interruption recovery, duplicate prevention, artifact integrity, stale-data handling, saved-key reuse, secret exclusion, TypeScript checking, a production build and browser behaviour. Synthetic fixtures are isolated technical tests and are not included in research results.

```powershell
# From Hackathon 6
& '.\.venv\Scripts\python.exe' -m unittest discover -s tests -p 'test_*.py' -v
cd dashboard
npm.cmd test
npm.cmd run typecheck
npm.cmd run build
```

Operational details are documented in [automation/LIVE_CONNECTION.md](automation/LIVE_CONNECTION.md). Model evaluation results are documented in [EVALUATION_REPORT.md](EVALUATION_REPORT.md).
