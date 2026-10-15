"""Real local-model test on explicitly synthetic test inputs, never research data."""
import json
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sentiment.core import Classifier, LABELS

if __name__ == "__main__":
    start = time.monotonic()
    model = Classifier(Path(__file__).resolve().parents[1] / ".model-cache")
    texts = ["I love this technology. Self-driving cars are wonderful!",
             "The video describes a self-driving car driving along a road.",
             "This is terrible and unsafe. I hate these dangerous cars.",
             "This video is about cars. " * 600]
    inference_start = time.monotonic()
    predictions = model.predict(texts)
    inference_seconds = time.monotonic() - inference_start
    assert len(predictions) == len(texts)
    assert all(label in LABELS and 0 <= confidence <= 1 for label, confidence in predictions)
    report = {"test_data": "Synthetic smoke-test inputs; not collected comments or ground truth", "model": model.version,
              "device": model.device, "seconds": round(time.monotonic() - start, 2), "inference_seconds": round(inference_seconds, 3),
              "predictions": [{"sentiment": label, "confidence": score} for label, score in predictions]}
    output = Path(__file__).parent / "model_smoke_report.json"
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
