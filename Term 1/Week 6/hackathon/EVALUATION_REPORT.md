# Sentiment model evaluation — 14 October 2026

The completed human annotation workbook and two explicitly supplied chat labels provide **60 annotated real comments**. Nine were labelled Not relevant and excluded from the sentiment comparison. Both models were evaluated on the same **51 relevant comments**: 26 Negative, 17 Neutral, and 8 Positive.

Human labels describe attitudes toward autonomous driving. RoBERTa and VADER classify general text sentiment, so disagreement can reflect target-specific meaning, sarcasm, ambiguity, or annotation judgement. The human labels were preserved without automatic correction.

| Model | Matches with human labels | Accuracy on this sample | Disagreements |
| --- | ---: | ---: | ---: |
| CardiffNLP Twitter RoBERTa | 32 / 51 | 62.7% | 19 |
| VADER 3.3.2 | 17 / 51 | 33.3% | 34 |

RoBERTa revision: `3216a57f2a0d9c45a2e6c20157c20c49fb4bf9c7`. VADER uses compound scores with Positive ≥ 0.05, Negative ≤ −0.05, and Neutral otherwise. Accuracy is measured agreement with this annotator on this small, relevance-filtered sample; it is not verified accuracy on all collected comments or all public opinion. Model confidence is not accuracy.

## Confusion matrices

Rows are human labels. Columns are model predictions.

### RoBERTa

| Actual / Predicted | Negative | Neutral | Positive |
| --- | ---: | ---: | ---: |
| Negative | 18 | 6 | 2 |
| Neutral | 5 | 11 | 1 |
| Positive | 3 | 2 | 3 |

### VADER

| Actual / Predicted | Negative | Neutral | Positive |
| --- | ---: | ---: | ---: |
| Negative | 13 | 3 | 10 |
| Neutral | 7 | 3 | 7 |
| Positive | 3 | 4 | 1 |

## Three documented RoBERTa failures

These explanations come from the annotator's explicit chat replies. They document disagreement with that annotator's interpretation; they are not independently verified universal ground truth.

1. **“😂😂😂 Technology gonna save us!!”** — human Neutral, model Positive. The annotator interprets the comment as sarcasm rather than literal praise. The original human Neutral label is retained.
2. **“C'mon guys you could've hit it with your high intensity water hose. That would've been great.”** — human Negative, model Positive. The annotator sees an endorsement of damaging the vehicle with water because of its electronics. Positive wording about the imagined outcome does not express support for the vehicle.
3. **“Talk about a ‘smart’ car... 😂😂 sawing a log in through middle of the street. 😂 back and forth, back and forth.. 😂 real smart.”** — human Negative, model Positive. The annotator identifies “smart” as sarcastic mockery of the vehicle's behaviour.

## Provenance and checks

- Original workbook: `C:/Users/luuka/Downloads/manual_labels_simple.xlsx`; unchanged SHA-256 `b0013e174a489575fa9d959035f993322efd5bfab6035c439b71e51999877fcf`.
- All 60 IDs and texts match the original collected comments. The 58 workbook labels were imported as entered; two initially empty labels were completed by explicit human replies (Neutral and Negative).
- Manual labels remain separate in `data/manual_labels.csv`. Three optional failure explanations are stored there and retain their verbatim human source in `data/failure_explanations.json`.
- Evaluation calculations and source hashes are in `data/evaluation.json`; import provenance is in `data/manual_labels_import.json`.
- Independently checked the 32 RoBERTa matches, 17 VADER matches, matrix totals, and input hashes. No transformer retraining or replacement of stored predictions was performed.
- Evaluation status is ready: at least 50 matched relevant labels and three supplied human failure explanations are present.

View the comparison at [the evaluation page](http://localhost:3101/evaluation).
