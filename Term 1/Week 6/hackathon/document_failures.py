"""Attach supplied human explanations to verified model-label disagreements."""
import argparse
import json
from pathlib import Path
from sentiment.core import atomic_csv, read_rows, RESULT_COLUMNS

BASE=Path(__file__).resolve().parent

def document(labels_path, results_path, explanations_path):
    labels=read_rows(labels_path,["comment_id","text","manual_sentiment"])
    results=read_rows(results_path,RESULT_COLUMNS)
    payload=json.loads(explanations_path.read_text(encoding="utf-8"))
    for identifier, entry in payload["explanations"].items():
        if identifier not in labels or identifier not in results:
            raise ValueError("Explanation refers to a comment without both a manual label and prediction")
        if labels[identifier]["manual_sentiment"] not in {"Positive","Neutral","Negative"}:
            raise ValueError("A failure explanation requires a relevant manual sentiment label")
        if labels[identifier]["manual_sentiment"]==results[identifier]["sentiment"]:
            raise ValueError("Explanation does not correspond to an observed model-label disagreement")
        if not entry["explanation"].strip(): raise ValueError("Failure explanation must not be empty")
    for identifier, entry in payload["explanations"].items():
        labels[identifier]["notes"]=entry["explanation"]
    atomic_csv(labels_path,["comment_id","text","manual_sentiment","notes"],labels.values())
    return len(payload["explanations"])

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--labels",type=Path,default=BASE/'data/manual_labels.csv')
    parser.add_argument("--results",type=Path,default=BASE/'data/sentiment_results.csv')
    parser.add_argument("--explanations",type=Path,default=BASE/'data/failure_explanations.json')
    args=parser.parse_args()
    print(f"Documented {document(args.labels,args.results,args.explanations)} verified disagreements using supplied human explanations.")
